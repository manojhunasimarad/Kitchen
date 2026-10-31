"""Assemble the app's data (recipes, pantry, track, week, reference) into data.json."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
import json
import re
from book1_extra import B1_EXTRA

# ------------------------------------------------------------------ pantry
# (key, label, group, default state) — 0 have, 1 low, 2 out
PANTRY = [
    ("atta", "Whole-wheat atta", "Grains and flours", 0), ("rice", "Sona masoori rice", "Grains and flours", 0),
    ("basmati", "Basmati rice", "Grains and flours", 0), ("seeraga", "Seeraga samba rice", "Grains and flours", 2),
    ("ragi", "Ragi flour", "Grains and flours", 2), ("poha", "Thick poha", "Grains and flours", 0),
    ("rava", "Rava (semolina)", "Grains and flours", 2), ("besan", "Besan", "Grains and flours", 0),
    ("ricefl", "Rice flour", "Grains and flours", 2), ("cornflour", "Cornflour", "Grains and flours", 2),
    ("bread", "Bread", "Grains and flours", 2), ("papad", "Papad", "Grains and flours", 2),
    ("toor", "Toor dal", "Dals, beans and nuts", 0), ("moongdal", "Split yellow moong dal", "Dals, beans and nuts", 0),
    ("wmoong", "Whole green moong", "Dals, beans and nuts", 0), ("chanadal", "Chana dal", "Dals, beans and nuts", 0),
    ("uraddal", "Urad dal", "Dals, beans and nuts", 0), ("rajma", "Rajma", "Dals, beans and nuts", 2),
    ("kchana", "Kabuli chana", "Dals, beans and nuts", 2), ("soya", "Soya chunks", "Dals, beans and nuts", 0),
    ("rchana", "Roasted chana (putani)", "Dals, beans and nuts", 0), ("peanuts", "Raw peanuts", "Dals, beans and nuts", 0),
    ("cashews", "Cashews", "Dals, beans and nuts", 2), ("makhana", "Makhana", "Dals, beans and nuts", 2),
    ("flax", "Flaxseeds", "Dals, beans and nuts", 2), ("sesame", "Sesame seeds", "Dals, beans and nuts", 2),
    ("eggs", "Eggs", "Dairy and eggs", 0), ("milk", "Milk", "Dairy and eggs", 0), ("curd", "Curd", "Dairy and eggs", 0),
    ("paneer", "Paneer", "Dairy and eggs", 2), ("ghee", "Ghee", "Dairy and eggs", 0), ("butter", "Butter", "Dairy and eggs", 2),
    ("cream", "Fresh cream", "Dairy and eggs", 2),
    ("chicken", "Chicken, bone-in", "Fresh protein (buy on the day)", 2),
    ("chickenbl", "Chicken, boneless", "Fresh protein (buy on the day)", 2),
    ("mince", "Chicken mince", "Fresh protein (buy on the day)", 2), ("fish", "Fish", "Fresh protein (buy on the day)", 2),
    ("prawns", "Prawns", "Fresh protein (buy on the day)", 2), ("mutton", "Mutton", "Fresh protein (buy on the day)", 2),
    ("onion", "Onions", "Vegetables and herbs", 0), ("tomato", "Tomatoes", "Vegetables and herbs", 0),
    ("potato", "Potatoes", "Vegetables and herbs", 0), ("ginger", "Ginger", "Vegetables and herbs", 0),
    ("garlic", "Garlic", "Vegetables and herbs", 0), ("greenchilli", "Green chillies", "Vegetables and herbs", 0),
    ("lemon", "Lemons", "Vegetables and herbs", 0), ("coriander", "Coriander leaves", "Vegetables and herbs", 1),
    ("mint", "Mint", "Vegetables and herbs", 2), ("curryleaves", "Curry leaves", "Vegetables and herbs", 1),
    ("spinach", "Spinach", "Vegetables and herbs", 2), ("cabbage", "Cabbage", "Vegetables and herbs", 2),
    ("beans", "Beans", "Vegetables and herbs", 2), ("carrot", "Carrots", "Vegetables and herbs", 0),
    ("cauliflower", "Cauliflower", "Vegetables and herbs", 2), ("bhindi", "Bhindi (okra)", "Vegetables and herbs", 2),
    ("mushrooms", "Mushrooms", "Vegetables and herbs", 2), ("capsicum", "Capsicum", "Vegetables and herbs", 2),
    ("peas", "Green peas", "Vegetables and herbs", 2), ("cucumber", "Cucumber", "Vegetables and herbs", 2),
    ("sambarveg", "Sambar vegetables (drumstick, pumpkin, brinjal)", "Vegetables and herbs", 2),
    ("coconut", "Coconut (fresh or desiccated)", "Vegetables and herbs", 2),
    ("springonion", "Spring onions", "Vegetables and herbs", 2),
    ("longchilli", "Long mild chillies (bajji)", "Vegetables and herbs", 2),
    ("turmeric", "Turmeric", "Spices and masalas", 0), ("chilli", "Red chilli powder", "Spices and masalas", 0),
    ("kashmiri", "Kashmiri chilli powder", "Spices and masalas", 0),
    ("coriander_p", "Coriander powder or seeds", "Spices and masalas", 0),
    ("cumin", "Cumin seeds", "Spices and masalas", 0), ("cumin_p", "Roasted cumin powder", "Spices and masalas", 0),
    ("garam", "Garam masala", "Spices and masalas", 0), ("mustard", "Mustard seeds", "Spices and masalas", 0),
    ("hing", "Hing", "Spices and masalas", 0), ("kasuri", "Kasuri methi", "Spices and masalas", 0),
    ("chaat", "Chaat masala", "Spices and masalas", 0), ("amchur", "Amchur", "Spices and masalas", 2),
    ("pepper", "Black pepper", "Spices and masalas", 0), ("fennel", "Fennel seeds", "Spices and masalas", 0),
    ("methi_s", "Methi seeds", "Spices and masalas", 0), ("ajwain", "Ajwain", "Spices and masalas", 2),
    ("wholespice", "Whole spices (bay leaf, cinnamon, cloves, cardamom)", "Spices and masalas", 0),
    ("shahijeera", "Shahi jeera", "Spices and masalas", 2), ("redchilli", "Dried red chillies", "Spices and masalas", 0),
    ("biryanimasala", "Biryani masala", "Spices and masalas", 2), ("sambarpowder", "Sambar powder", "Spices and masalas", 0),
    ("bbbpowder", "Bisi bele bath powder", "Spices and masalas", 2), ("cholemasala", "Chole masala", "Spices and masalas", 2),
    ("saffron", "Saffron", "Spices and masalas", 2), ("kewra", "Kewra or rose water", "Spices and masalas", 2),
    ("tamarind", "Tamarind", "Spices and masalas", 0), ("jaggery", "Jaggery", "Spices and masalas", 0),
    ("sugar", "Sugar", "Spices and masalas", 0), ("soysauce", "Soy sauce and vinegar", "Spices and masalas", 2),
    ("coconutmilk", "Coconut milk (tetra pack)", "Spices and masalas", 2), ("oil", "Cooking oil", "Spices and masalas", 0),
]
KEYS = {k for k, *_ in PANTRY}
SOFT = {"coriander", "cream", "kasuri", "chaat", "sugar", "lemon", "saffron", "kewra", "springonion", "cashews",
        "redchilli", "mint"}

RULES = [  # (regex on lowercased ingredient name, keys); every matching rule contributes
    (r"ginger-garlic", ["ginger", "garlic"]), (r"\bginger\b(?!-)", ["ginger"]), (r"\bgarlic\b", ["garlic"]),
    (r"kashmiri chilli", ["kashmiri"]), (r"red chilli powder|(?<!kashmiri )\bchilli powder", ["chilli"]),
    (r"green chilli", ["greenchilli"]), (r"dried red chill|byadgi", ["redchilli"]),
    (r"long mild green chill", ["longchilli"]),
    (r"coriander powder|coriander seeds", ["coriander_p"]), (r"coriander(?! powder| seeds)", ["coriander"]),
    (r"roasted cumin|cumin powder", ["cumin_p"]), (r"cumin seeds|^cumin$", ["cumin"]), (r"shahi jeera", ["shahijeera"]),
    (r"spring onion", ["springonion"]), (r"\bonions?\b(?!.*rings)", ["onion"]), (r"tomato", ["tomato"]),
    (r"potato", ["potato"]), (r"lemon", ["lemon"]), (r"\bmint\b", ["mint"]), (r"curry leaves", ["curryleaves"]),
    (r"spinach", ["spinach"]), (r"cauliflower", ["cauliflower"]), (r"bhindi|okra", ["bhindi"]),
    (r"mushroom", ["mushrooms"]), (r"capsicum", ["capsicum"]), (r"green peas", ["peas"]), (r"cucumber", ["cucumber"]),
    (r"coconut milk", ["coconutmilk"]), (r"coconut(?! milk| oil)", ["coconut"]),
    (r"mixed vegetables|vegetables, finely chopped", ["carrot|beans|peas|capsicum|cauliflower"]),
    (r"carrot", ["carrot"]),
    (r"toor dal", ["toor"]), (r"split yellow moong", ["moongdal"]), (r"whole green moong", ["wmoong"]),
    (r"urad dal", ["uraddal"]), (r"chana dal", ["chanadal"]), (r"rajma", ["rajma"]), (r"kabuli chana", ["kchana"]),
    (r"roasted chana", ["rchana"]), (r"soya", ["soya"]), (r"peanut", ["peanuts"]), (r"cashew", ["cashews"]),
    (r"makhana", ["makhana"]), (r"flaxseed", ["flax"]), (r"sesame", ["sesame"]),
    (r"atta", ["atta"]), (r"ragi flour", ["ragi"]), (r"poha", ["poha"]), (r"\brava\b", ["rava"]), (r"besan", ["besan"]),
    (r"rice flour", ["ricefl"]), (r"sona masoori or basmati", ["rice|basmati"]), (r"basmati", ["basmati"]),
    (r"sona masoori rice$|^sona masoori rice", ["rice"]), (r"seeraga", ["seeraga"]), (r"bread", ["bread"]),
    (r"phulkas or parathas", ["atta"]), (r"cornflour", ["cornflour"]), (r"papad", ["papad"]),
    (r"\beggs?\b", ["eggs"]), (r"(?<!coconut )(?<!warm )\bmilk\b", ["milk"]), (r"curd", ["curd"]), (r"paneer", ["paneer"]),
    (r"\bghee\b", ["ghee"]), (r"butter", ["butter"]), (r"cream", ["cream"]),
    (r"chicken, bone-in|bone-in chicken", ["chicken"]), (r"chicken mince|keema", ["mince"]),
    (r"boneless chicken|chicken breast|chicken thigh", ["chickenbl"]), (r"\bfish\b", ["fish"]),
    (r"prawn", ["prawns"]), (r"mutton", ["mutton"]),
    (r"turmeric", ["turmeric"]), (r"garam masala or biryani masala", ["garam|biryanimasala"]),
    (r"garam masala", ["garam"]), (r"biryani masala", ["biryanimasala"]), (r"mustard seeds", ["mustard"]),
    (r"mustard oil", ["oil"]), (r"\bhing\b", ["hing"]), (r"kasuri methi", ["kasuri"]), (r"chaat masala", ["chaat"]),
    (r"amchur", ["amchur"]), (r"black pepper|peppercorns|white pepper", ["pepper"]), (r"fennel", ["fennel"]),
    (r"methi \(fenugreek\) seeds|methi seeds", ["methi_s"]), (r"ajwain", ["ajwain"]),
    (r"bay leaf|cinnamon|cloves(?! ,)|cardamom|star anise|mace", ["wholespice"]), (r"saffron", ["saffron"]),
    (r"kewra|rose water", ["kewra"]), (r"sambar powder", ["sambarpowder"]), (r"bisi bele bath powder", ["bbbpowder"]),
    (r"chole masala", ["cholemasala"]), (r"tamarind", ["tamarind"]), (r"jaggery", ["jaggery"]),
    (r"\bsugar\b", ["sugar"]), (r"soy sauce|vinegar", ["soysauce"]), (r"\boil\b(?! for frying)|oil for frying", ["oil"]),
]
# garlic cloves "Garlic cloves" -> garlic only; avoid "cloves" whole spice matching it
SKIP_GROUP = re.compile(r"\(optional\)|^to serve|^or ", re.I)


def needs_from(ingredients, extra_names=()):
    keys = []
    for g in ingredients:
        if SKIP_GROUP.search(g["group"] or ""):
            continue
        for it in g["items"]:
            name, note = it["name"], it.get("note", "")
            if "optional" in note.lower() or "optional" in name.lower():
                continue
            keys += match(name)
    for n in extra_names:
        if "optional" not in n.lower():
            keys += match(n)
    out = []
    for k in keys:
        if k not in out:
            out.append(k)
    return out


FAT_OR = re.compile(r"\b(oil|ghee|butter)\b\s*\(?or (?:melted )?\b(oil|ghee|butter)\b")
SKIP_NAME = re.compile(r"for the seal|for sealing|^warm milk", re.I)


def match(name):
    low = name.lower()
    if SKIP_NAME.search(low):
        return []
    m = FAT_OR.search(low)
    if m:
        return [m.group(1) + "|" + m.group(2)]
    found = []
    for rx, ks in RULES:
        if re.search(rx, low):
            if rx.startswith("bay leaf") and "garlic cloves" in low:
                continue
            found += ks
    ors = [k for k in found if "|" in k]
    members = {x for k in ors for x in k.split("|")}
    return [k for k in found if "|" in k or k not in members]


def minutes(t):
    h = re.search(r"(\d+)\s*h\b", t)
    m = re.search(r"(\d+)\s*min", t)
    total = (int(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m and (not h or m.start() > h.start()) else 0)
    if not h and m:
        total = int(m.group(1))
    return total or None


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48]


def pnum(p):
    m = re.search(r"(\d+)", p or "")
    return int(m.group(1)) if m else None


CHAPTER_SHORT = {"Breads and rice": "Breads and rice", "Breakfasts": "Breakfasts", "Dals and beans": "Dals and beans",
                 "Vegetables": "Vegetables", "Paneer, eggs and soya": "Paneer, eggs and soya",
                 "Chicken, fish and mutton": "Chicken, fish and mutton",
                 "Air fryer and sandwich maker": "Air fryer and sandwich maker",
                 "Chutneys, podis and raitas": "Chutneys, podis and raitas"}

recipes = []

# ------------------------------------------------------------------ Book 2 cards
for c in json.load(open(ROOT / "data" / "b2_cards.json")):
    ch = c["chips"]
    base = {
        "book": 2, "page": c["page"], "chapter": c["chapter"], "time": ch.get("TIME", ""),
        "serving": ch.get("ONE SERVING") or ch.get("MAKES", ""), "protein": ch.get("PROTEIN", ""),
        "oil": ch.get("ADDED OIL", ""), "keeps": ch.get("KEEPS", ""), "uses": ch.get("USES", ""),
    }
    if c["subs"]:
        for s in c["subs"]:
            r = dict(base)
            r.update({"id": slug(s["name"]), "title": s["name"], "sub": c["title"], "intro": s["meta"],
                      "parentIntro": c["intro"], "ingredients": [{"group": "", "items": [
                          {"name": x, "note": "", "q": ""} for x in s["ing"]]}], "plainIng": True,
                      "steps": [s["method"]] if s["method"] else [], "tips": [], "var": [], "cues": [], "why": "",
                      "serve": "", "note": "", "batch": True})
            pm = re.search(r"(\d+)(?:–\d+)? g of protein", s["meta"])
            r["protein"] = f"~{pm.group(1)} g" if pm else ("~1–2 g" if "chutney" in c["title"].lower() else
                                                           ("~2 g per tbsp" if "powder" in c["title"].lower() else ""))
            r["needs"] = needs_from([], s["ing"])
            if c["title"].startswith("Sandwich"):
                r["needs"] = [k for k in r["needs"] if k != "butter"]
            recipes.append(r)
        continue
    r = dict(base)
    r.update({"id": slug(c["title"]), "title": c["title"], "sub": c["sub"], "intro": c["intro"],
              "ingredients": c["ingredients"], "steps": c["steps"], "tips": c["tips"], "var": c["var"],
              "cues": c["cues"], "why": c["why"], "serve": c["serve"], "note": c["note"], "batch": c["batch"]})
    r["needs"] = needs_from(c["ingredients"])
    recipes.append(r)

# ------------------------------------------------------------------ Book 1 masters
B1_META = {
    "Andhra-Style Chicken Dum Biryani": ("andhra-chicken-biryani", "Spicy, layered, sealed on dum", "~30 g", "1 plate",
                                         "3 burners (air fryer optional)"),
    "Lucknowi (Awadhi) Paneer Biryani": ("lucknowi-paneer-biryani", "Mild, creamy and perfumed", "~28 g", "1 plate",
                                         "3 burners (air fryer optional)"),
    "Bengaluru Donne-Style Mushroom Biryani": ("donne-mushroom-biryani", "Green, peppery, one-pot", "~12 g", "1 plate",
                                               "3 burners (air fryer optional)"),
    "Chicken + Paneer for Five": ("party-chicken-paneer-biryani", "Two biryanis from one shared base", "",
                                  "5 (3 chicken, 2 paneer)", "4 burners"),
}
for m in json.load(open(ROOT / "data" / "b1_masters.json")):
    rid, sub, prot, serving, uses = B1_META[m["title"]]
    for g in m["ingredients"]:
        g["group"] = g["group"].replace("\x00 chicken, \x00 paneer", "two-thirds chicken, one-third paneer")
    r = {"id": rid, "book": 1, "page": m["page"], "chapter": "Master biryanis", "title": m["title"], "sub": sub,
         "time": m["chips"].get("TOTAL", ""), "hands": m["chips"].get("HANDS-ON", ""), "serving": serving,
         "protein": prot, "oil": "", "uses": uses, "intro": m["intro"], "ingredients": m["ingredients"],
         "steps": [f'{s["title"]}. {s["text"]}' for s in m["steps"]],
         "stepMeta": [s["meta"] for s in m["steps"]], "tips": [{"title": t["title"], "text": t["text"]}
                                                              for t in m["tips"]],
         "var": [], "cues": [], "why": "", "serve": "", "note": "", "batch": m["batch"]}
    r["needs"] = needs_from(m["ingredients"])
    recipes.append(r)

for e in B1_EXTRA:
    r = dict(e)
    r.update({"book": 1, "oil": "", "var": [], "cues": [], "why": "", "serve": "", "note": "", "batch": True})
    r["steps"] = list(e["steps"])
    recipes.append(r)

# ------------------------------------------------------------------ overrides and derived fields
OVERRIDE_NEEDS = {
    "paratha-plain-or-stuffed": ["atta", "ghee|oil", "paneer|potato", "greenchilli", "onion"],
    "palya": ["beans|cabbage|carrot", "oil", "mustard", "uraddal", "curryleaves", "coconut", "turmeric"],
    "egg-paneer-kathi-rolls": ["atta", "eggs", "paneer", "onion", "capsicum", "oil", "mint", "greenchilli"],
    "sambar": ["toor", "sambarveg|carrot|beans", "tamarind", "sambarpowder", "jaggery", "oil", "mustard", "methi_s",
               "curryleaves", "hing", "turmeric"],
    "bisi-bele-bath": ["toor", "rice", "carrot|beans|peas|capsicum", "tamarind", "bbbpowder", "ghee", "mustard",
                       "curryleaves", "hing", "turmeric"],
    "egg-bhurji-sandwich": ["bread", "eggs", "onion", "tomato", "greenchilli"],
    "paneer-bhurji-sandwich": ["bread", "paneer", "onion", "tomato"],
    "paneer-tikka-sandwich": ["bread", "paneer", "curd", "onion"],
    "omelette-pockets-no-bread": ["eggs", "onion", "tomato"],
    "bombay-veg-masala-toast": ["bread", "potato", "cucumber", "tomato", "onion", "mint"],
    "phulka-toastie": ["atta", "paneer|eggs"],
    "green-chutney-mint-coriander": ["coriander", "mint", "greenchilli", "lemon"],
    "masala-peanuts-roasted-chana-and-makhana": ["peanuts|rchana|makhana"],
    "raitas-and-kachumber": ["curd", "cucumber"],
    "rice-cooked-right": ["rice|basmati"],
}
OVERRIDE_STRICT = {
    "green-chutney-mint-coriander": ["coriander", "mint", "greenchilli"],
    "andhra-chicken-biryani": None, "donne-mushroom-biryani": None,
}
OVERRIDE_STRICT = {k: v for k, v in OVERRIDE_STRICT.items() if v}
for r in recipes:
    if r["id"] in OVERRIDE_NEEDS:
        r["needs"] = OVERRIDE_NEEDS[r["id"]]
    bad = [k for n in r["needs"] for k in n.split("|") if k not in KEYS]
    assert not bad, (r["id"], bad)
    r["strict"] = OVERRIDE_STRICT.get(r["id"]) or [n for n in r["needs"] if not all(k in SOFT for k in n.split("|"))]
    meat = {"chicken", "chickenbl", "mince", "fish", "prawns", "mutton"}
    flat = {k for n in r["needs"] for k in n.split("|")}
    firsts = {n.split("|")[0] for n in r["needs"]}
    if firsts & meat or (flat & meat and not (flat - meat) & {"paneer"}):
        r["diet"] = "nonveg" if firsts & meat or any(set(n.split("|")) <= meat for n in r["needs"]) else "veg"
    else:
        r["diet"] = "veg"
    if r["diet"] == "veg" and any(set(n.split("|")) == {"eggs"} for n in r["needs"]):
        r["diet"] = "egg"
    if r["id"] in ("shami-kebab",):
        r["diet"] = "nonveg"
    r["minutes"] = minutes(r.get("time", ""))
    r["proteinNum"] = pnum(r.get("protein", ""))
    text = " ".join([r.get("uses", "")] + r["steps"] + r.get("var", []) +
                    [t["title"] + " " + t["text"] for t in r.get("tips", [])]).lower()
    tags = []
    if "air fryer" in r.get("uses", "").lower():
        tags.append("airfryer")
    elif "air-fry" in text or "air fryer" in text:
        tags.append("airfryer-option")
    if "sandwich maker" in r.get("uses", "").lower():
        tags.append("sandwich")
    elif "sandwich maker" in text:
        tags.append("sandwich-option")
    if "cooker" in r.get("uses", "").lower():
        tags.append("cooker")
    if r["minutes"] and r["minutes"] <= 20 and "soak" not in r.get("time", "") and "day" not in r.get("time", ""):
        tags.append("quick")
    if r["id"] in ("bisi-bele-bath", "soya-pulao", "egg-fried-rice", "egg-paneer-kathi-rolls"):
        tags.append("lunchbox")
    r["tags"] = tags

ids = [r["id"] for r in recipes]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
RID = set(ids)

# ------------------------------------------------------------------ the track (stages)
def row(rid=None, label=None, ref=None, note=None, key=None):
    if rid:
        assert rid in RID, rid
        return {"id": "r-" + rid, "recipe": rid}
    return {"id": "t-" + key, "label": label, "ref": ref, "note": note or ""}


TRACK = [
    {"title": "Set up the kitchen", "when": "Week 1",
     "note": "The habits everything else depends on. Do these before cooking anything new.",
     "rows": [row(key="pantry", label="Fill in your pantry in the Pantry tab", ref="App"),
              row(key="curd", label="Set curd overnight, three nights running", ref="Book 2 p. 11"),
              row(key="cooker", label="Check the cooker gasket and vent; learn the whistle chart", ref="Book 2 p. 12"),
              row(key="knife", label="Slice an onion 2–3 mm with the grain, and dice one", ref="Book 1 p. 9"),
              row("air-fryer-boiled-eggs")]},
    {"title": "Rice and dal", "when": "Week 1–2",
     "note": "The everyday base. Pass each one when it's right three times in a row.",
     "rows": [row("rice-cooked-right"),
              row(key="pip", label="Pot-in-pot: dal and rice together in one cooker", ref="Book 2 p. 13"),
              row("moong-dal"), row("dal-tadka"), row("sambar")]},
    {"title": "Fast breakfasts", "when": "Week 2",
     "note": "Protein that keeps without a fridge: eggs, dals, besan, peanuts.",
     "rows": [row("egg-bhurji-and-masala-omelette"), row("besan-chilla"), row("moong-dal-chilla"),
              row("kanda-poha-with-peanuts"), row("sprout-chaat")]},
    {"title": "Phulka and breads", "when": "Week 3",
     "note": "Where the most time goes, and the biggest saving once the rhythm is in your hands.",
     "rows": [row("phulka-soft-chapati"),
              row(key="rhythm", label="Phulka rhythm: 4 phulkas in 5 minutes", ref="Book 2 p. 27",
                  note="Roll the next while one is on the tawa."),
              row("paratha-plain-or-stuffed"), row("ragi-rotti")]},
    {"title": "Vegetables", "when": "Week 3–4", "note": "Half the plate.",
     "rows": [row("palya"), row("aloo-gobi"), row("bhindi-masala"), row("mushroom-pepper-fry")]},
    {"title": "Paneer and eggs", "when": "Week 4",
     "note": "Paneer is bought on the day; eggs carry the weekday mornings.",
     "rows": [row("paneer-bhurji"), row("palak-paneer"), row("paneer-butter-masala"), row("egg-curry"),
              row(key="paneer", label="Make paneer at home from 1 litre of milk", ref="Book 2 p. 11")]},
    {"title": "Lunch-box one-pots and beans", "when": "Week 5",
     "note": "Packed piping hot into a preheated insulated box.",
     "rows": [row("bisi-bele-bath"), row("soya-pulao"), row("egg-fried-rice"), row("rajma-masala"), row("chole")]},
    {"title": "Chicken, fish and mutton", "when": "Week 5–6",
     "note": "Bought on the way home and cooked within two hours.",
     "rows": [row("home-style-chicken-curry"), row("pepper-chicken-fry"), row("butter-chicken"),
              row("coastal-fish-curry"), row("mutton-curry"), row("egg-paneer-kathi-rolls")]},
    {"title": "Air fryer and sandwich maker", "when": "Week 6–7",
     "note": "High protein, a teaspoon of oil, and no standing at the stove.",
     "rows": [row("air-fryer-tandoori-chicken"), row("air-fryer-paneer-tikka"), row("air-fryer-chicken-seekh-kebab"),
              row("air-fryer-fish-rava-fry"), row("air-fryer-hara-bhara-kabab"), row("air-fryer-soya-cutlets"),
              row("masala-peanuts-roasted-chana-and-makhana"), row("egg-bhurji-sandwich"),
              row("omelette-pockets-no-bread")]},
    {"title": "Chutneys and keepers", "when": "Week 7",
     "note": "Small things that make plain food taste finished; the powders keep for weeks.",
     "rows": [row("green-chutney-mint-coriander"), row("coconut-chutney"), row("shenga-chutney-pudi-peanut"),
              row("gunpowder-idli-podi"), row("raitas-and-kachumber")]},
    {"title": "Run the default week", "when": "Week 8",
     "note": "Two weeks without changing anything: the sessions become automatic.",
     "rows": [row(key="week1", label="Cook every meal of one default week", ref="This week tab"),
              row(key="week2", label="Cook a second default week, same plan", ref="This week tab"),
              row(key="morningA", label="Morning A in 40 minutes or less", ref="Book 2 p. 19"),
              row(key="dinner1", label="Dinner 1 in 40 minutes or less", ref="Book 2 p. 22")]},
    {"title": "Biryani foundations", "when": "Week 9",
     "note": "The eight master techniques from Book 1, practised one at a time.",
     "rows": [row(key="birista", label="Birista: deep golden, not dark", ref="Book 1 p. 13",
                  note="Stove or air fryer."),
              row(key="marinade", label="A curd marinade that coats like thick batter", ref="Book 1 p. 14"),
              row(key="parboil", label="Par-boil basmati to exactly 75%", ref="Book 1 p. 15"),
              row(key="dum", label="Layer, seal with dough and dum on the tawa", ref="Book 1 p. 16"),
              row("jeera-rice"), row("ghee-rice")]},
    {"title": "Master biryanis", "when": "Week 10–11",
     "note": "Score each one with the five-star scorecard (Reference). 32 out of 40 is hotel grade.",
     "rows": [row("andhra-chicken-biryani"), row("lucknowi-paneer-biryani"), row("donne-mushroom-biryani"),
              row("air-fryer-chicken-65"), row("mirchi-ka-salan"), row("burani-raita"), row("double-ka-meetha")]},
    {"title": "Variations and the hotel finish", "when": "Week 12+",
     "note": "Same masala, new protein. Then cook for friends.",
     "rows": [row("chicken-donne-biryani"), row("andhra-egg-biryani"), row("lucknowi-chicken-biryani"),
              row("mutton-biryani"), row("fish-biryani"), row("prawn-biryani"), row("soya-biryani"),
              row("lean-chicken-donne"), row("shami-kebab"),
              row(key="dhungar", label="Charcoal smoke finish (dhungar)", ref="Book 1 p. 57"),
              row("party-chicken-paneer-biryani")]},
]

# ------------------------------------------------------------------ the default week
WEEK = [
    {"day": "Mon", "night": "Set curd.", "buy": ["Bone-in chicken 200 g", "Tomato", "Cucumber"],
     "session": "Morning A · Dinner 2 (Book 2 p. 19, 23)",
     "meals": [("b", "Moong dal chilla + 2 boiled eggs", 26, "moong-dal-chilla"),
               ("l", "Bisi bele bath + curd", 20, "bisi-bele-bath"),
               ("d", "Chicken curry + 4 phulkas + kachumber", 43, "home-style-chicken-curry")], "total": 104},
    {"day": "Tue", "night": "Set curd.", "buy": ["Small cabbage", "Coriander"],
     "session": "Morning B · Dinner 1 (Book 2 p. 20, 22)",
     "meals": [("b", "2 egg-bhurji sandwiches", 28, "egg-bhurji-sandwich"),
               ("l", "Soya pulao + cucumber raita", 21, "soya-pulao"),
               ("d", "Dal tadka + rice + cabbage palya + curd", 25, "dal-tadka")], "total": 88},
    {"day": "Wed", "night": "Set curd. Soak split yellow moong dal for Thursday.", "buy": ["Paneer 100 g", "Spinach"],
     "session": "Morning C · Dinner 3 (Book 2 p. 21, 24)",
     "meals": [("b", "Kanda poha with peanuts + milk", 16, "kanda-poha-with-peanuts"),
               ("l", "Egg fried rice", 23, "egg-fried-rice"),
               ("d", "Palak paneer + 4 phulkas", 35, "palak-paneer")], "total": 90},
    {"day": "Thu", "night": "Set curd. Tomorrow morning: soak kabuli chana before you leave.",
     "buy": ["Chicken breast 175 g", "Lemons", "Cucumber"], "session": "Morning A · Dinner 4 (Book 2 p. 19, 25)",
     "meals": [("b", "Moong dal chilla + 2 boiled eggs", 26, "moong-dal-chilla"),
               ("l", "Bisi bele bath + curd", 20, "bisi-bele-bath"),
               ("d", "Air-fryer tandoori chicken + moong dal + kachumber", 57, "air-fryer-tandoori-chicken")],
     "total": 118},
    {"day": "Fri", "night": "Set curd. Soak whole green moong for Sunday's sprouts.",
     "buy": ["Onions, tomatoes, coriander"], "session": "Morning B (Book 2 p. 20)",
     "meals": [("b", "2 egg-bhurji sandwiches", 28, "egg-bhurji-sandwich"),
               ("l", "Soya pulao + cucumber raita", 21, "soya-pulao"),
               ("d", "Chole + 4 phulkas + onion salad", 26, "chole")], "total": 90},
    {"day": "Sat", "night": "Set curd. Drain the moong into a damp cloth to sprout.",
     "buy": ["Morning: paneer 75 g, fish 150 g, beans"], "session": "Weekend",
     "meals": [("b", "Paneer paratha + curd", 29, "paratha-plain-or-stuffed"),
               ("l", "Fish curry + rice + beans palya", 39, "coastal-fish-curry"),
               ("d", "Egg curry + 4 phulkas", 32, "egg-curry")], "total": 116},
    {"day": "Sun", "night": "Set curd. Soak split yellow moong dal for Monday.",
     "buy": ["Morning: chicken for biryani, paneer 100 g, capsicum, mint, coriander"], "session": "Weekend",
     "meals": [("b", "Sprout chaat + 2 boiled eggs", 26, "sprout-chaat"),
               ("l", "Andhra chicken biryani + raita", 33, "andhra-chicken-biryani"),
               ("d", "Air-fryer paneer tikka + 4 phulkas + kachumber", 35, "air-fryer-paneer-tikka")], "total": 109},
]
for d in WEEK:
    for m in d["meals"]:
        assert m[3] in RID, m

# ------------------------------------------------------------------ reference
REFERENCE = {
    "cooker": [["Toor dal", "20–30 min (optional)", "1 : 3", "3 soaked; 4–5 unsoaked"],
               ["Split yellow moong dal", "None", "1 : 3", "2"], ["Masoor dal", "None", "1 : 3", "2"],
               ["Chana dal", "1 hour", "1 : 3", "3–4"], ["Whole green moong", "6–8 hours", "1 : 3", "3"],
               ["Rajma", "8–10 hours", "1 : 4", "1 on high, then 20 min lowest"],
               ["Kabuli chana", "8–10 hours", "1 : 4", "1 on high, then 15 min lowest"],
               ["Sona masoori rice", "Optional, 10 min", "1 : 2", "3"], ["Basmati rice", "15–20 min", "1 : 1½", "1"],
               ["Bisi bele bath, khichdi", "—", "about 1 : 4½", "4 (khichdi 3)"],
               ["Chicken curry, bone-in", "—", "¾ cup", "2"], ["Mutton curry", "—", "1 cup", "5–6 (young goat 4–5)"]],
    "airfryer": [["Boiled eggs", "130 °C", "15 min (jammy 12–13)"], ["Tandoori chicken, breast chunks", "200 °C", "12–14 min"],
                 ["Boneless chicken (tikka, 65)", "200 °C", "12–14 min"], ["Seekh kebab", "200 °C", "12–14 min"],
                 ["Paneer tikka", "200 °C", "8–10 min"], ["Fish rava fry", "200 °C", "10–12 min"],
                 ["Mushrooms", "200 °C", "8–10 min"], ["Bhindi", "190 °C", "10–12 min"],
                 ["Aloo gobi", "200 °C", "15–18 min"], ["Birista (1 onion, 1 tbsp oil)", "160 °C", "15–25 min"],
                 ["Masala peanuts", "160 °C", "12–15 min"], ["Makhana", "150 °C", "8–10 min"],
                 ["Paratha (¼ tsp ghee a side)", "200 °C", "about 4 min a side"]],
    "keeps": [["Onions, potatoes, garlic", "2–4 weeks"], ["Ginger", "1–2 weeks"], ["Tomatoes", "3–5 days"],
              ["Carrots, cabbage", "4–7 days"], ["Beans, bhindi, capsicum", "2–3 days"],
              ["Spinach, greens", "Same day"], ["Eggs", "7–10 days, cool spot"], ["Curd", "About 12 hours after setting"],
              ["Paneer, chicken, fish, mutton", "Cook within 2 hours of buying"],
              ["Cooked food", "Eat within 2 hours, or keep hot in an insulated box"],
              ["Phulkas", "Until next morning, wrapped"], ["Chutney powders, roasted snacks", "2–4 weeks, airtight"]],
    "boosters": [["2 boiled eggs", "+12 g"], ["100 g paneer", "+18 g"], ["25 g soya chunks", "+13 g"],
                 ["250 ml milk", "+8 g"], ["30 g roasted chana", "+7 g"], ["30 g masala peanuts", "+8 g"],
                 ["An egg on a phulka", "+6 g each"]],
    "jars": [
        {"name": "Tandoori jar", "jar": "2 tbsp Kashmiri chilli, 2 tsp each of garam masala, roasted cumin, coriander "
         "powder, crushed kasuri methi, amchur and salt, 1 tsp turmeric.",
         "use": "1½ tbsp of the mix, 3 tbsp thick curd, 1 tsp ginger-garlic paste, 1 tsp mustard oil, half a lemon."},
        {"name": "Kali mirch jar", "jar": "2 tbsp freshly crushed black pepper, 2 tsp each of roasted cumin, coriander "
         "powder, kasuri methi and salt, 1 tsp cardamom powder.",
         "use": "1 heaped tbsp of the mix, 3 tbsp curd, 1 tbsp cashew paste or cream, 1 tsp ginger-garlic paste, "
                "1 tsp lemon juice."},
        {"name": "Achari jar", "jar": "Dry-roast 4 tsp fennel, 2 tsp mustard seeds, 2 tsp cumin, 1 tsp methi seeds and "
         "1 tsp nigella; cool and crush coarsely. Add 4 tsp Kashmiri chilli, 2 tsp amchur, 2 tsp salt, 1 tsp turmeric.",
         "use": "1½ tbsp of the mix, 3 tbsp curd, 1 tbsp mustard oil, 1 tsp ginger-garlic paste."}],
    "brands": [["Kilrr tikka packs", "Chicken; paneer and mushrooms with 20-minute marination"],
               ["Suhana Chicken Tikka, Paneer Tikka, Butter Chicken", "Single-meal spice mixes"],
               ["Mother's Recipe / Rasoi Magic Paneer Tikka", "Paneer, mushrooms, soya"],
               ["Ching's Secret Masala Chicken, Paneer Chilli, Manchurian", "Indo-Chinese sachets"],
               ["Aachi / Sakthi Chicken 65 masala", "Chicken, gobi, paneer, egg 65"],
               ["Aachi / Everest Egg Curry masala", "Egg curry"],
               ["MDH / Everest Tandoori masala", "Chicken, paneer or egg tikka"],
               ["Keya Piri Piri seasoning", "Omelettes, eggs, air-fried paneer"]],
    "scorecard": [["Grains", "Long, separate and whole"], ["A plain grain from the top", "Seasoned and fragrant on its own"],
                  ["Colour", "Clear white, gold and orange-brown grains"], ["Protein", "Juicy and tender; soft paneer"],
                  ["Masala", "Clings to every piece, no pooling"], ["Bottom layer", "Moist and lightly toasted"],
                  ["Aroma on opening", "Fills the room"], ["Oil", "Glossy, not oily"]],
    "safety": ["Buy chicken, fish, mutton, paneer and curd on the day; start cooking meat within two hours.",
               "Marinate covered in the coolest spot, never longer than 2 hours.",
               "Eat cooked food within 2 hours, or pack it piping hot into a preheated insulated box.",
               "Never keep cooked rice overnight without a fridge.",
               "Rajma must be soaked, drained and cooked until a bean mashes completely.",
               "Steam sprouts 4–5 minutes before eating."],
}

data = {"recipes": recipes, "pantry": [{"key": k, "label": l, "group": g, "def": d} for k, l, g, d in PANTRY],
        "soft": sorted(SOFT), "track": TRACK, "week": WEEK, "ref": REFERENCE}
json.dump(data, open(ROOT / "data" / "data.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(recipes), "recipes;", sum(len(s["rows"]) for s in TRACK), "track rows;",
      round(len(json.dumps(data, ensure_ascii=False)) / 1024), "KB")
for r in recipes:
    print(f'{r["book"]} {r["page"]:3d} {r["diet"]:6s} {str(r["minutes"]):4s} {r["protein"]:>16s} '
          f'{r["id"][:34]:34s} {",".join(r["tags"]):26s} {" ".join(r["strict"])}')
