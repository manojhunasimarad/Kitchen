"""What was checked, what was fixed, and against which sources (shown in the app under Reference)."""

AUDIT = {
    "date": "31 Oct 2026",
    "limits": "No video transcripts were available to check against, and videos can't be watched here. The two books "
              "were written for you earlier in this same chat, so matching them shows the app copied them faithfully, "
              "not that they are right. The independent checks are the published recipes and food-safety sources "
              "below.",
    "summary": [
        "All 77 book recipes in the app were compared line by line with the two PDFs: every ingredient name, "
        "quantity and method step matches. The 20 Book 1 variations and sides are correctly halved from the book's "
        "2-serving amounts.",
        "Every one of the 109 recipes was checked automatically for ingredients missing from the list or never used, "
        "salt levels, air-fryer temperatures, marinating longer than 2 hours without a fridge, doneness checks for "
        "meat and fish, rice and rajma safety, and leftovers.",
        "Key numbers (cooker whistles, soaking, par-boiling, air-fryer settings, safe temperatures) were compared "
        "with published recipes and food-safety guidance. They agree, apart from the fixes listed below.",
    ],
    "fixed": [
        "Book 1 variations: 8 ingredient rows the book has but the app had left out were added: salt, turmeric and "
        "lemon in both donne marinades, the egg rub for egg biryani, oil for the potatoes in veg biryani, salt for "
        "ghee rice and veg pulao, turmeric, chilli and salt for mirchi ka salan, and coriander for chitranna.",
        "Chicken fried rice used rice cooked that morning. Without a fridge, cooked rice must be eaten or fried "
        "within 2 hours, so the method now cooks the rice, steams it dry and fries it straight away.",
        "Egg and pepper pasta set the eggs with leftover heat only. It now thickens over the lowest flame to about "
        "70 °C, so the eggs are cooked through but still creamy.",
        "Thai red curry said tulsi is the basil Thai cooks use. Thai sweet basil goes in red curry (holy basil is for "
        "dishes like pad kra pao), so it now lists Thai basil, with Italian basil or tulsi as stand-ins.",
        "Air-fryer falafel: time corrected to 16–18 minutes at 190 °C (was 14–16), and the soak to 12–24 hours.",
        "Six chicken recipes now say how to tell the chicken is done (no pink inside; 74 °C with a thermometer).",
        "Salt cut in three recipes that came out at 1,900–2,400 mg sodium a serving: less salt in the pasta water "
        "and sauces, and no extra salt in the chilli chicken marinade, since the soy sauce is salty.",
        "Nutrition for phulka toastie now includes salt.",
    ],
    "checks": [
        ["Rajma soaking and cooking", "Soak overnight; 1 whistle on high, then 20 min on the lowest flame, until a "
         "bean mashes completely", "Soak 8–12 h; 4–5 whistles until a bean mashes easily. FDA: soak at least 5 h "
         "and boil hard; the toxin is destroyed at 100 °C in 10 min", "Agrees", "ihr-rajma osu-beans"],
        ["Dal in the pressure cooker", "Toor 1 : 3, 3 whistles soaked, 4–5 unsoaked; moong 2", "Soaked 2–3, "
         "unsoaked 3–4 whistles; 1 : 2.5–3", "Agrees (upper end, fine in a 3 L cooker)", "prestige wonderchef"],
        ["Kabuli chana", "Soak 8–10 h; 1 whistle on high, then 15 min low", "Soak overnight, 4–5 whistles",
         "Agrees", "prestige"],
        ["Rice in the cooker", "Sona masoori 1 : 2, 3 whistles", "1 : 2, 2–3 whistles", "Agrees", "prestige"],
        ["Mutton curry", "Check at 4 whistles; young goat 3–4, older 5–6", "5–6, up to 8 for tough cuts",
         "Agrees", "prestige"],
        ["Bone-in chicken curry", "2 whistles", "About 3–4 for bone-in", "Low end: if the meat doesn't leave the "
         "bone easily, give it one more whistle", "prestige"],
        ["Dum biryani", "Par-boil rice to 75%; dum 15–20 min; rest 10", "Par-boil to 70%; dum 15 min; rest 15–20",
         "Agrees", "vismai"],
        ["Marinating without a fridge", "Never more than 2 hours", "2 h, or overnight only in a fridge",
         "Agrees (the safe limit without a fridge)", "vismai ihr-paneer"],
        ["Air-fryer boiled eggs", "130 °C, 15 min (jammy 12–13)", "121 °C (250 °F), 15–17 min", "Agrees",
         "skinnytaste"],
        ["Air-fryer paneer tikka", "200 °C, 8–10 min", "200 °C, about 7 min", "Agrees (bigger cubes take longer)",
         "ihr-paneer"],
        ["Air-fryer falafel", "Soaked raw chana; 190 °C 14–16 min", "Dried chickpeas soaked 20–24 h, never cooked; "
         "190 °C 16–18 min, turned at 10", "Fixed", "elmundo"],
        ["Chicken doneness", "White right through, clear juices", "Poultry 74 °C (165 °F); fish 63 °C or until it "
         "flakes", "Agrees; checks added", "hawaii"],
        ["Cooked rice without a fridge", "Eat within 2 hours; never overnight", "Keep above 60 °C or eat at once; "
         "reheating does not destroy the B. cereus toxin", "Agrees; fried rice fixed", "mpi"],
        ["Basil in Thai red curry", "Tulsi", "Thai basil in red and green curries; holy basil in kra pao-style "
         "stir-fries", "Fixed", "wiki-basil"],
        ["Egg pasta sauce", "Eggs set by the pasta's heat", "Sauce thickens about 65 °C; eggs set 62–70 °C; use "
         "pasteurised eggs for a runny sauce", "Fixed", "gavin"],
    ],
    "sources": {
        "ihr-rajma": ["Indian Healthy Recipes: Rajma masala", "https://www.indianhealthyrecipes.com/rajma-recipe-rajma-masala/"],
        "osu-beans": ["Ohio State University: Dry kidney beans need to be boiled", "https://cfaes.osu.edu/news/articles/chow-line-dry-kidney-beans-need-be-boiled"],
        "prestige": ["TTK Prestige: How many whistles", "https://shop.ttkprestige.com/blog/post/tips-and-tricks/how-many-whistles-a-pressure-cooker-timing-guide"],
        "wonderchef": ["Wonderchef: How to cook dal in a pressure cooker", "https://www.wonderchef.com/blogs/recipes/how-to-cook-dal-in-a-pressure-cooker-perfect-every-time-for-tadka-khichdi"],
        "vismai": ["Vismai Food: Hyderabadi chicken dum biryani", "https://vismaifood.com/hyderabadi-chicken-dum-biryani-how-to-make-hyderabadi-chicken-dum-biryani"],
        "ihr-paneer": ["Indian Healthy Recipes: Paneer tikka (oven, air fryer, stovetop)", "https://www.indianhealthyrecipes.com/wprm_print/paneer-tikka-recipe-in-oven-air-fryer-stovetop"],
        "skinnytaste": ["Skinnytaste: Air fryer hard-boiled eggs", "https://www.skinnytaste.com/air-fryer-hard-boiled-eggs"],
        "elmundo": ["El Mundo Eats: Crispy air fryer falafel", "https://www.elmundoeats.com/crispy-air-fryer-falafel-gluten-free-vegan/"],
        "hawaii": ["Hawaii Dept. of Health: Safe minimum temperatures", "https://health.hawaii.gov/food-drug/files/2024/02/Food-Safety-Minimum-Temperatures-1.pdf"],
        "mpi": ["NZ Ministry for Primary Industries: Bacillus cereus in rice", "https://www.mpi.govt.nz/food-safety-home/food-poisoning-symptoms-causes/bacillus-cereus-bacteria-rice-starchy-food"],
        "wiki-basil": ["Wikipedia: Thai basil", "https://en.wikipedia.org/wiki/Thai_basil"],
        "gavin": ["Jessica Gavin: Pasta carbonara", "https://www.jessicagavin.com/pasta-carbonara/"],
    },
}

# sources behind the calculator, blood-test ranges and hair-fall guide
HEALTH_SOURCES = [
    ["ICMR-NIN 2020 dietary allowances (summary)", "https://open-exam-prep.com/study-guides/in-osssc-staff-nurse/basic-nursing-sciences/nutrition-dietetics"],
    ["Revised definition of obesity in Asian Indians (2025)", "https://www.cmcendovellore.org/pub/2025/revised-definition-of-obesity-in-asian-indians-living-in-india.pdf"],
    ["ISSN position stand: protein and exercise", "https://pubmed.ncbi.nlm.nih.gov/28642676/"],
    ["American Academy of Dermatology: Hair shedding", "https://www.aad.org/public/diseases/hair-loss/insider/shedding"],
    ["Biotin interference with lab tests (HSA, citing the US FDA)", "https://www.hsa.gov.sg/announcements/biotin-interference-with-clinical-laboratory-tests/"],
    ["Rosemary oil vs minoxidil 2% trial (Panahi et al., 2015)", "https://eprints.bmsu.ac.ir/738"],
]
