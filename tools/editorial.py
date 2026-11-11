"""Versioned pilot preparation metadata, not a claim of kitchen-tested accuracy."""
import re

SOURCES = {
    "chilla-technique": {"title": "Dassana Amit: Moong Dal Chilla", "url": "https://www.vegrecipesofindia.com/moong-dal-chilla-recipe/", "checked": "2026-11-06", "scope": "Split yellow lentil soaking, grinding and consistency; a different yield/variant, not validation of this entire recipe."},
    "safe-temperatures": {"title": "FoodSafety.gov: Minimum internal temperatures", "url": "https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures", "checked": "2026-11-06", "scope": "Poultry doneness: use a thermometer; 74 °C in the thickest part. Raw eggs: whites and yolks firm."},
}

# Durations retained from recipe text unless specifically noted; trials are still needed.
PILOT = {
 "phulka-soft-chapati": ([0,0], [], [], "Four phulkas per serving. Resting is included in the existing 35-minute estimate; extra batches take longer."),
 "paratha-plain-or-stuffed": (None, ["Choose paneer or aloo filling. For aloo, boil, cool enough to handle and mash potatoes before starting."], [], "40 minutes assumes the filling ingredients are prepared. Nutrition currently represents the paneer variant."),
 "rice-cooked-right": (None, ["Choose sona masoori or basmati; follow its water ratio and soak instructions."], [], "The 25-minute estimate does not establish a measured raw-start time for every rice/cooker combination. Include natural pressure release."),
 "moong-dal-chilla": ([180,240], ["Rinse split yellow moong, soak for 3–4 hours, drain, then grind. The soaking water is separate from the grinding water."], ["chilla-technique"], "20 minutes after soaking is the existing estimate for two chillas; grinding, pan setup and additional batches vary."),
 "rajma-masala": ([480,600], ["Soak dried rajma for 8–10 hours as specified in this recipe, then drain and use fresh cooking water."], [], "The existing 60-minute cooking estimate includes pressure cooking and masala preparation; pressure release and bean age vary."),
 "chole": ([480,600], ["Soak dried chickpeas for 8–10 hours, then drain before pressure cooking."], [], "Do not count unsoaked chickpeas as prepared. The existing 60-minute cooking estimate is not a measured guarantee."),
 "air-fryer-tandoori-chicken": ([45,135], ["Allow 15 minutes to strain the curd if it is not already hung. Marinate for 30 minutes to 2 hours in the refrigerator. Keep raw chicken separate from ready-to-eat ingredients."], ["safe-temperatures"], "The 25-minute cooking estimate assumes one uncrowded batch. Use 74 °C in the thickest part as the poultry endpoint, not colour alone."),
 "air-fryer-paneer-tikka": ([20,60], ["Marinate paneer for 20–60 minutes in the refrigerator. If using wooden skewers, soak them before use."], [], "30 minutes after marinating is the existing estimate. Air-fryer capacity determines batch count."),
 "air-fryer-falafel": ([720,1440], ["Start with dried chickpeas soaked for 12–24 hours and drained as specified in this recipe, not cooked chickpeas."], [], "35 minutes after soaking is the existing estimate for eight patties. Extra batches need additional cooking time."),
 "korean-egg-rice-bowl": (None, ["Cook the rice first using Rice, cooked right. Use freshly cooked rice; dry rice in the pantry is not a prepared bowl of rice."], ["safe-temperatures"], "10 minutes applies only after rice is cooked. The ingredient weight is a dry-rice equivalent, not the weight of the cooked rice."),
 "phulka-toastie": (None, ["Prepare the phulka, chosen bhurji filling and green chutney before assembling. Use freshly prepared ingredients."], [], "10 minutes is assembly/toasting only. If starting with raw ingredients, follow the linked component recipes first."),
 "andhra-chicken-biryani": (None, ["Read the complete sequence before starting: marinade, birista, rice soak, masala, par-boil, layering, dum and rest."], ["safe-temperatures"], "110 minutes is the existing multi-burner estimate; a one-burner schedule is not verified. Rice soaking can overlap only with independent tasks."),
}

DEPENDENCIES = {
 "phulka-toastie": ["phulka-soft-chapati", "paneer-bhurji", "green-chutney-mint-coriander"],
 "korean-egg-rice-bowl": ["rice-cooked-right"],
 "paratha-plain-or-stuffed": ["phulka-soft-chapati"],
}

def enrich(recipes):
    for r in recipes:
        if r.get("contentReview"):
            r["review"] = dict(r["contentReview"])
            r["dependencies"] = []
            r["methodSteps"] = [{"id": f"step-{i+1}", "instruction": text} for i,text in enumerate(r["steps"])]
            continue
        r["review"] = {"status": "Needs cooking validation", "version": 1, "kitchenTested": False}
        r["sources"] = []
        r["dependencies"] = DEPENDENCIES.get(r["id"], [])
        r["methodSteps"] = [{"id": f"step-{i+1}", "instruction": text} for i,text in enumerate(r["steps"])]
        if r["id"] in PILOT:
            wait, prerequisites, sources, note = PILOT[r["id"]]
            r["timing"] = {"cookMinutes": [r["minutes"],r["minutes"]], "prerequisiteMinutes": wait,
                           "prerequisites": prerequisites, "basis": "Existing recipe estimate; not measured", "note": note}
            r["sources"] = [SOURCES[k] for k in sources]
            r["review"]["status"] = "Preparation pilot · not kitchen-tested"
        else:
            # Unknown raw-start time must not become a confident quick-filter match.
            r["timing"] = {"cookMinutes": [r["minutes"],r["minutes"]] if r["minutes"] else None,
                           "prerequisiteMinutes": None, "prerequisites": [],
                           "basis": "Legacy recipe estimate; preparation not yet reviewed",
                           "note": "Check ingredients and all method steps before starting. Soaking, pre-cooking, marinating or extra batches may add time."}
    return recipes
