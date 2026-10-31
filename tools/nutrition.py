"""Nutrition data and the gram converter.

NUTR holds approximate values per 100 g of the food as bought (raw, dry), from USDA FoodData Central
and the Indian Food Composition Tables (IFCT 2017), rounded. Bone-in meat is per 100 g including bone.
Fields: kcal, protein g, carbs g, fat g, fibre g, iron mg, calcium mg, magnesium mg, zinc mg,
potassium mg, sodium mg, vitamin C mg, vitamin B12 µg.
"""
import re

FIELDS = ["kcal", "p", "c", "f", "fib", "fe", "ca", "mg", "zn", "k", "na", "vc", "b12"]

_N = {
    # grains and flours
    "atta":        (340, 13.2, 72, 2.5, 10.7, 3.6, 34, 137, 2.6, 363, 2, 0, 0),
    "rice":        (360, 6.8, 79, 0.6, 1.3, 0.8, 10, 25, 1.1, 115, 5, 0, 0),
    "basmati":     (356, 8.0, 78, 0.6, 1.0, 0.8, 10, 25, 1.1, 110, 1, 0, 0),
    "seeraga":     (355, 7.5, 78, 0.8, 1.5, 0.9, 12, 28, 1.1, 120, 3, 0, 0),
    "ragi":        (328, 7.3, 72, 1.3, 11.2, 3.9, 344, 137, 2.3, 408, 11, 0, 0),
    "poha":        (346, 6.6, 77, 1.2, 2.0, 2.6, 10, 30, 1.0, 120, 5, 0, 0),
    "rava":        (360, 12.7, 73, 1.0, 3.9, 1.2, 17, 47, 1.1, 186, 1, 0, 0),
    "besan":       (387, 22.4, 58, 6.7, 10.8, 4.9, 45, 166, 2.8, 846, 64, 0, 0),
    "ricefl":      (366, 6.0, 80, 1.4, 2.4, 0.4, 10, 35, 0.8, 76, 0, 0, 0),
    "cornflour":   (381, 0.3, 91, 0.1, 0.9, 0.5, 2, 3, 0.1, 3, 9, 0, 0),
    "bread":       (265, 9.0, 49, 3.2, 2.7, 1.5, 60, 25, 0.8, 120, 480, 0, 0),
    "oats":        (379, 13.2, 68, 6.5, 10.1, 4.3, 52, 138, 3.6, 362, 6, 0, 0),
    "pasta":       (371, 13.0, 75, 1.5, 3.2, 1.3, 21, 53, 1.4, 223, 6, 0, 0),
    "noodles":     (380, 12.0, 75, 1.5, 3.0, 1.5, 20, 40, 1.0, 150, 300, 0, 0),
    "papad":       (371, 25.6, 60, 3.3, 18.6, 7.6, 143, 271, 3.2, 1001, 1745, 0, 0),
    # dals, beans, nuts, seeds
    "toor":        (343, 22.0, 62, 1.5, 15.0, 4.0, 73, 183, 2.8, 1100, 17, 0, 0),
    "moongdal":    (348, 24.5, 59, 1.2, 8.2, 4.0, 75, 150, 2.7, 1000, 15, 0, 0),
    "wmoong":      (347, 23.9, 63, 1.2, 16.3, 6.7, 132, 189, 2.7, 1246, 15, 4.8, 0),
    "chanadal":    (360, 21.0, 60, 5.5, 15.0, 5.0, 56, 130, 3.0, 720, 30, 1, 0),
    "uraddal":     (341, 25.2, 59, 1.6, 18.3, 7.6, 138, 267, 3.4, 983, 38, 0, 0),
    "rajma":       (333, 23.6, 60, 0.8, 15.2, 6.5, 143, 140, 2.8, 1406, 24, 4.5, 0),
    "kchana":      (364, 19.3, 61, 6.0, 17.4, 6.2, 105, 115, 3.4, 875, 24, 4, 0),
    "soya":        (345, 52.0, 33, 0.5, 13.0, 9.2, 241, 290, 2.5, 2384, 20, 0, 0),
    "rchana":      (369, 22.5, 58, 5.2, 16.8, 5.0, 58, 140, 3.4, 846, 26, 0, 0),
    "peanuts":     (567, 25.8, 16, 49.2, 8.5, 4.6, 92, 168, 3.3, 705, 18, 0, 0),
    "cashews":     (553, 18.2, 30, 43.9, 3.3, 6.7, 37, 292, 5.8, 660, 12, 0.5, 0),
    "makhana":     (350, 9.7, 77, 0.1, 7.6, 1.4, 60, 67, 1.4, 500, 1, 0, 0),
    "flax":        (534, 18.3, 29, 42.2, 27.3, 5.7, 255, 392, 4.3, 813, 30, 0.6, 0),
    "sesame":      (570, 18.0, 23, 49.0, 11.0, 7.8, 130, 350, 7.0, 470, 11, 0, 0),
    "peanutbutter": (588, 25.0, 20, 50.0, 6.0, 1.9, 43, 154, 2.5, 649, 460, 0, 0),
    # dairy and eggs
    "eggs":        (143, 12.6, 0.7, 9.5, 0, 1.75, 56, 12, 1.3, 138, 142, 0, 0.89),
    "milk":        (58, 3.2, 4.8, 3.0, 0, 0.05, 120, 11, 0.4, 150, 44, 0, 0.45),
    "curd":        (60, 3.5, 4.7, 3.0, 0, 0.05, 121, 12, 0.6, 155, 46, 0.5, 0.37),
    "paneer":      (265, 18.3, 1.2, 20.8, 0, 0.2, 208, 26, 2.0, 100, 22, 0, 0.6),
    "ghee":        (900, 0, 0, 99.5, 0, 0, 4, 0, 0, 5, 2, 0, 0),
    "butter":      (717, 0.9, 0.1, 81, 0, 0, 24, 2, 0.1, 24, 643, 0, 0.17),
    "cream":       (250, 2.0, 3.5, 25, 0, 0, 70, 7, 0.2, 95, 35, 0.5, 0.2),
    "cheese":      (315, 20.0, 2.0, 25, 0, 0.3, 600, 25, 2.6, 130, 1250, 0, 1.0),
    # fresh protein (as bought)
    "chicken":     (100, 15.0, 0, 4.0, 0, 0.7, 9, 19, 1.4, 180, 65, 0, 0.3),
    "chickenbl":   (120, 22.5, 0, 2.6, 0, 0.5, 6, 28, 0.8, 330, 50, 0, 0.2),
    "mince":       (143, 17.4, 0, 8.1, 0, 0.8, 6, 21, 1.5, 522, 60, 0, 0.6),
    "fish":        (110, 19.0, 0, 3.0, 0, 0.8, 30, 30, 0.6, 380, 70, 0, 2.5),
    "prawns":      (85, 20.1, 0, 0.5, 0, 0.5, 64, 35, 1.1, 264, 150, 0, 1.1),
    "mutton":      (125, 14.5, 0, 7.5, 0, 2.0, 10, 18, 3.0, 280, 60, 0, 1.0),
    # vegetables, fruit and herbs
    "onion":       (40, 1.1, 9.3, 0.1, 1.7, 0.2, 23, 10, 0.2, 146, 4, 7.4, 0),
    "tomato":      (18, 0.9, 3.9, 0.2, 1.2, 0.3, 10, 11, 0.2, 237, 5, 13.7, 0),
    "potato":      (77, 2.0, 17.5, 0.1, 2.2, 0.8, 12, 23, 0.3, 425, 6, 19.7, 0),
    "ginger":      (80, 1.8, 17.8, 0.8, 2.0, 0.6, 16, 43, 0.3, 415, 13, 5, 0),
    "garlic":      (149, 6.4, 33, 0.5, 2.1, 1.7, 181, 25, 1.2, 401, 17, 31, 0),
    "greenchilli": (40, 2.0, 9.5, 0.2, 1.5, 1.2, 18, 25, 0.3, 340, 7, 240, 0),
    "lemon":       (22, 0.4, 6.9, 0.2, 0.3, 0.1, 6, 6, 0.05, 103, 1, 38.7, 0),
    "coriander":   (23, 2.1, 3.7, 0.5, 2.8, 1.8, 67, 26, 0.5, 521, 46, 27, 0),
    "mint":        (70, 3.8, 15, 0.9, 8.0, 5.1, 243, 80, 1.1, 569, 31, 31.8, 0),
    "tulsi":       (23, 3.2, 2.7, 0.6, 1.6, 3.2, 177, 64, 0.8, 295, 4, 18, 0),
    "curryleaves": (108, 6.1, 18.7, 1.0, 6.4, 0.9, 830, 44, 0.2, 300, 10, 4, 0),
    "spinach":     (23, 2.9, 3.6, 0.4, 2.2, 2.7, 99, 79, 0.5, 558, 79, 28, 0),
    "cabbage":     (25, 1.3, 5.8, 0.1, 2.5, 0.5, 40, 12, 0.2, 170, 18, 36.6, 0),
    "beans":       (31, 1.8, 7.0, 0.2, 2.7, 1.0, 37, 25, 0.2, 211, 6, 12.2, 0),
    "carrot":      (41, 0.9, 9.6, 0.2, 2.8, 0.3, 33, 12, 0.2, 320, 69, 5.9, 0),
    "cauliflower": (25, 1.9, 5.0, 0.3, 2.0, 0.4, 22, 15, 0.3, 299, 30, 48, 0),
    "bhindi":      (33, 1.9, 7.5, 0.2, 3.2, 0.6, 82, 57, 0.6, 299, 7, 23, 0),
    "mushrooms":   (22, 3.1, 3.3, 0.3, 1.0, 0.5, 3, 9, 0.5, 318, 5, 2.1, 0.04),
    "capsicum":    (20, 0.9, 4.6, 0.2, 1.7, 0.3, 10, 10, 0.1, 175, 3, 80, 0),
    "peas":        (81, 5.4, 14.5, 0.4, 5.7, 1.5, 25, 33, 1.2, 244, 5, 40, 0),
    "cucumber":    (15, 0.7, 3.6, 0.1, 0.5, 0.3, 16, 13, 0.2, 147, 2, 2.8, 0),
    "sambarveg":   (30, 1.2, 6.5, 0.2, 2.5, 0.5, 25, 15, 0.2, 230, 5, 20, 0),
    "coconut":     (354, 3.3, 15.2, 33.5, 9.0, 2.4, 14, 32, 1.1, 356, 20, 3.3, 0),
    "springonion": (32, 1.8, 7.3, 0.2, 2.6, 1.5, 72, 20, 0.4, 276, 16, 18.8, 0),
    "longchilli":  (30, 1.5, 6.5, 0.2, 2.0, 0.8, 15, 20, 0.2, 280, 5, 100, 0),
    "sweetcorn":   (86, 3.3, 19, 1.4, 2.0, 0.5, 2, 37, 0.5, 270, 15, 6.8, 0),
    "banana":      (89, 1.1, 22.8, 0.3, 2.6, 0.3, 5, 27, 0.15, 358, 1, 8.7, 0),
    "vegmix":      (35, 1.8, 7.0, 0.2, 2.6, 0.6, 30, 18, 0.3, 250, 20, 30, 0),
    # spices and masalas
    "turmeric":    (312, 9.7, 67, 3.3, 22.7, 55, 168, 208, 4.5, 2080, 27, 0.7, 0),
    "chilli":      (318, 12.0, 57, 17.3, 27.2, 7.8, 148, 152, 2.5, 2014, 30, 76, 0),
    "kashmiri":    (318, 12.0, 57, 17.3, 27.2, 7.8, 148, 152, 2.5, 2014, 30, 76, 0),
    "redchilli":   (318, 12.0, 57, 17.3, 27.2, 7.8, 148, 152, 2.5, 2014, 30, 76, 0),
    "coriander_p": (298, 12.4, 55, 17.8, 41.9, 16.3, 709, 330, 4.7, 1267, 35, 21, 0),
    "cumin":       (375, 17.8, 44, 22.3, 10.5, 66.4, 931, 366, 4.8, 1788, 168, 7.7, 0),
    "cumin_p":     (375, 17.8, 44, 22.3, 10.5, 66.4, 931, 366, 4.8, 1788, 168, 7.7, 0),
    "shahijeera":  (375, 17.8, 44, 22.3, 10.5, 66.4, 931, 366, 4.8, 1788, 168, 7.7, 0),
    "garam":       (379, 15.0, 45, 15, 30, 33, 500, 300, 3.5, 1500, 80, 10, 0),
    "biryanimasala": (350, 12.0, 45, 12, 28, 25, 450, 250, 3.0, 1400, 3000, 8, 0),
    "cholemasala": (330, 11.0, 48, 10, 25, 20, 400, 220, 2.5, 1300, 4000, 8, 0),
    "sambarpowder": (330, 14.0, 50, 9, 20, 15, 300, 200, 2.5, 1300, 1500, 5, 0),
    "bbbpowder":   (330, 14.0, 50, 9, 20, 15, 300, 200, 2.5, 1300, 1500, 5, 0),
    "mustard":     (508, 26.0, 28, 36, 12.2, 9.2, 266, 370, 6.1, 738, 13, 7.1, 0),
    "hing":        (300, 4.0, 68, 1, 4, 39, 690, 0, 0, 0, 0, 0, 0),
    "kasuri":      (323, 23.0, 58, 6.4, 24.6, 33.5, 176, 191, 2.5, 770, 67, 3, 0),
    "methi_s":     (323, 23.0, 58, 6.4, 24.6, 33.5, 176, 191, 2.5, 770, 67, 3, 0),
    "chaat":       (250, 8.0, 50, 4, 15, 20, 300, 150, 2, 1000, 15000, 0, 0),
    "amchur":      (330, 2.5, 80, 1.5, 5, 2, 60, 30, 0.2, 300, 20, 0, 0),
    "pepper":      (251, 10.4, 64, 3.3, 25.3, 9.7, 443, 171, 1.2, 1329, 20, 0, 0),
    "fennel":      (345, 15.8, 52, 14.9, 39.8, 18.5, 1196, 385, 4.0, 1694, 88, 21, 0),
    "ajwain":      (305, 16.0, 43, 25, 39, 16, 1525, 300, 3, 1200, 20, 0, 0),
    "wholespice":  (300, 7.0, 60, 8, 30, 15, 500, 200, 2, 1000, 50, 10, 0),
    "herbs":       (265, 9.0, 69, 4.3, 42.5, 36.8, 1597, 270, 2.7, 1260, 25, 2.3, 0),
    "saffron":     (0,) * 13, "kewra": (0,) * 13, "water": (0,) * 13,
    "tamarind":    (239, 2.8, 62.5, 0.6, 5.1, 2.8, 74, 92, 0.1, 628, 28, 3.5, 0),
    "jaggery":     (383, 0.4, 98, 0.1, 0, 2.6, 80, 70, 0.2, 1050, 30, 0, 0),
    "sugar":       (387, 0, 100, 0, 0, 0.05, 1, 0, 0, 2, 1, 0, 0),
    "honey":       (304, 0.3, 82, 0, 0.2, 0.4, 6, 2, 0.2, 52, 4, 0.5, 0),
    "soysauce":    (53, 8.1, 4.9, 0.6, 0.8, 1.5, 33, 40, 0.4, 435, 5493, 0, 0),
    "vinegar":     (18, 0, 0.04, 0, 0, 0, 6, 1, 0, 2, 2, 0, 0),
    "ketchup":     (101, 1.0, 27, 0.1, 0.3, 0.4, 15, 13, 0.2, 281, 907, 4, 0),
    "chillisauce": (120, 2.0, 20, 4, 2, 1, 20, 20, 0.2, 200, 2500, 5, 0),
    "currypaste":  (100, 2.0, 12, 5, 4, 3, 50, 30, 0.5, 300, 3000, 5, 0),
    "coconutmilk": (197, 2.0, 2.8, 21.3, 0, 1.6, 18, 46, 0.6, 220, 13, 1, 0),
    "oil":         (884, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "salt":        (0, 0, 0, 0, 0, 0, 24, 1, 0, 8, 38758, 0, 0),
    "raisins":     (299, 3.1, 79, 0.5, 3.7, 1.9, 50, 32, 0.2, 749, 11, 2.3, 0),
    "cocoa":       (228, 19.6, 58, 13.7, 37, 13.9, 128, 499, 6.8, 1524, 21, 0, 0),
}
NUTR = {k: dict(zip(FIELDS, v)) for k, v in _N.items()}

# grams per teaspoon, by what is measured (a tablespoon is 3 tsp, a cup is 48 tsp unless CUP says otherwise)
TSP = {"oil": 4.5, "ghee": 4.7, "butter": 4.7, "salt": 6, "sugar": 4.2, "jaggery": 5, "honey": 7, "curd": 5,
       "cream": 5, "milk": 5, "lemon": 5, "soysauce": 5.5, "vinegar": 5, "ketchup": 6, "chillisauce": 6,
       "tamarind": 5, "ginger": 5, "garlic": 5, "coconut": 2.5, "coconutmilk": 5, "peanutbutter": 5.3,
       "cumin": 2.1, "shahijeera": 2.1, "mustard": 3.4, "fennel": 2, "methi_s": 3.7, "ajwain": 2.2,
       "sesame": 3, "flax": 3.5, "pepper": 2.3, "wholespice": 2, "kasuri": 0.6, "coriander": 0.4, "mint": 0.4,
       "curryleaves": 0.4, "springonion": 1.5, "atta": 2.6, "besan": 2.3, "ricefl": 2.6, "cornflour": 2.7,
       "rava": 3.5, "oats": 1.7, "peanuts": 3, "cashews": 3, "chanadal": 4, "uraddal": 4, "herbs": 0.5,
       "currypaste": 5, "cocoa": 2, "redchilli": 1}
POWDER_TSP = 2.5
CUP = {"rice": 190, "basmati": 185, "seeraga": 185, "toor": 200, "moongdal": 200, "wmoong": 195, "chanadal": 200,
       "uraddal": 200, "rajma": 185, "kchana": 200, "atta": 125, "besan": 90, "ragi": 110, "rava": 170,
       "ricefl": 130, "poha": 80, "oats": 80, "curd": 245, "milk": 245, "peanuts": 145, "coconut": 80,
       "soya": 45, "rchana": 140, "makhana": 15, "vegmix": 120, "cabbage": 90, "beans": 110, "carrot": 120,
       "peas": 145, "spinach": 30, "coriander": 16, "mint": 16, "onion": 160, "tomato": 180, "cucumber": 120,
       "sambarveg": 120, "cauliflower": 107, "mushrooms": 70, "capsicum": 150, "coconutmilk": 240,
       "sweetcorn": 150, "cream": 240}
# grams for one counted item ("2 onions", "1 medium tomato"); size words scale it
EACH = {"onion": 110, "tomato": 100, "potato": 150, "eggs": 50, "greenchilli": 3, "lemon": 15, "garlic": 4,
        "bread": 28, "longchilli": 25, "redchilli": 0.5, "wholespice": 0.3, "capsicum": 120, "carrot": 60,
        "cucumber": 200, "banana": 100, "papad": 12, "cauliflower": 500, "springonion": 15, "peanuts": 0.6,
        "curryleaves": 0.1, "mint": 0.1, "tulsi": 0.1, "coriander": 0.1, "cashews": 1.5, "pepper": 0.06,
        "ginger": 6, "atta": 30, "kchana": 0.3, "tamarind": 3}
SIZE = {"small": 0.7, "medium": 1.0, "large": 1.35, "big": 1.35}

FRAC = {"½": .5, "¼": .25, "¾": .75, "⅓": 1 / 3, "⅔": 2 / 3, "⅛": .125}
NUM = r"(?:\d+(?:\.\d+)?(?:\s*[½¼¾⅓⅔⅛])?|[½¼¾⅓⅔⅛])"


def num(s):
    s = s.strip()
    total = 0.0
    m = re.match(r"(\d+(?:\.\d+)?)", s)
    if m:
        total += float(m.group(1))
        s = s[m.end():].strip()
    if s and s[0] in FRAC:
        total += FRAC[s[0]]
    return total


def parse_qty(q):
    """Return (amount, unit-ish rest) for the first quantity in q; ranges give their midpoint."""
    q = q.strip()
    low = q.lower()
    if not low or low.startswith(("as you like", "to taste")):
        return None, ""
    if low.startswith("a pinch") or low.startswith("pinch"):
        return 1, "pinch"
    if low.startswith("a few"):
        return 3, low[5:].strip()
    if low.startswith(("a little", "a squeeze", "a dash")):
        return 1, "tsp"
    if low.startswith("a handful"):
        return 1, "handful"
    m = re.match(rf"({NUM})(?:\s*[–-]\s*({NUM}))?\s*(.*)$", q)
    if not m:
        m2 = re.match(r"(\d+)\s*/\s*(\d+)\s*(.*)$", q)
        if m2:
            return int(m2.group(1)) / int(m2.group(2)), m2.group(3)
        return None, q
    a = num(m.group(1))
    if m.group(2):
        a = (a + num(m.group(2))) / 2
    return a, m.group(3)


def grams(key, q):
    """Grams of ingredient `key` for quantity text `q`, or None if it can't be read."""
    amt, rest = parse_qty(q)
    if amt is None:
        return None
    rest = rest.lower().strip()
    unit = re.match(r"(kg|g|ml|l|tsp|tbsp|cups?|inch(?:es)?|cloves?|pinch(?:es)?|sprigs?|slices?|leaves|handful|"
                    r"small|medium|large|big|batch)?\b", rest)
    u = unit.group(1) if unit else None
    if u is None and rest.startswith("l") and re.match(r"l\b", rest):
        u = "l"
    if u == "kg":
        return amt * 1000
    if u == "g":
        return amt
    if u in ("ml", "l"):
        dens = {"oil": .92, "ghee": .91, "milk": 1.03, "curd": 1.03, "coconutmilk": 1.0, "cream": 1.0}.get(key, 1.0)
        return amt * (1000 if u == "l" else 1) * dens
    if u in ("tsp", "tbsp", "cup", "cups"):
        t = TSP.get(key, POWDER_TSP)
        if u == "tbsp":
            return amt * t * 3
        if u.startswith("cup"):
            return amt * CUP.get(key, t * 48)
        return amt * t
    if u and u.startswith("inch"):
        return amt * {"ginger": 6, "wholespice": 1}.get(key, 5)
    if u and u.startswith("clove"):
        return amt * (4 if key == "garlic" else 0.1)
    if u and u.startswith("pinch"):
        return amt * 0.3
    if u and u.startswith("slice") and key == "ginger":
        return amt * 6
    if u and (u.startswith("sprig") or u == "leaves"):
        return amt * 0.5
    if u == "handful":
        return amt * {"peanuts": 30, "cashews": 25}.get(key, 15)
    if u and u.startswith("slice"):
        return amt * EACH.get(key, 28)
    if u == "batch":
        return amt * 20 if key == "onion" else None  # a batch of birista is about 20 g fried onion
    size = SIZE.get(u, 1.0) if u in SIZE else 1.0
    if key in EACH:
        return amt * EACH[key] * size
    if key in SPICES:
        return amt * 0.3
    return None


SPICES = {"wholespice", "shahijeera", "cumin", "pepper", "fennel", "mustard", "methi_s", "ajwain", "redchilli",
          "saffron", "kewra", "hing", "turmeric", "garam", "chilli", "kashmiri", "coriander_p"}


# ingredient name -> [(nutrition key, share)]; first matching rule wins
NAME_RULES = [
    (r"^water|^warm water|water for|^salt water|ice water|hot water|^ice\b|tea bag|food colou?r|for the seal|"
     r"for sealing|lemon wedges", []),
    (r"salt for the water|salt for boiling", [("salt", 0.1)]),
    (r"birista oil", [("oil", 1)]),
    (r"onion.*for birista", [("onion", 1)]),
    (r"\bbirista\b|fried onion", [("onion", 3), ("oil", 0.3)]),
    (r"raw papaya", [("vegmix", 1)]),
    (r"green masala|green chutney|dill|sabsige", [("coriander", 1)]),
    (r"^vegetable", [("vegmix", 1)]),
    (r"^eggs?\b|boiled eggs?", [("eggs", 1)]),
    (r"rajma|kidney bean", [("rajma", 1)]),
    (r"kabuli chana|chickpea", [("kchana", 1)]),
    (r"ginger-garlic|ginger garlic", [("ginger", .5), ("garlic", .5)]),
    (r"\bsalt\b", [("salt", 1)]),
    (r"kashmiri", [("kashmiri", 1)]),
    (r"chilli powder|spicy red chilli", [("chilli", 1)]),
    (r"dried red chill|byadgi|chilli flakes", [("redchilli", 1)]),
    (r"long mild|bajji", [("longchilli", 1)]),
    (r"green chill", [("greenchilli", 1)]),
    (r"coriander powder|coriander seeds", [("coriander_p", 1)]),
    (r"coriander|cilantro", [("coriander", 1)]),
    (r"roasted cumin|cumin powder", [("cumin_p", 1)]),
    (r"shahi jeera", [("shahijeera", 1)]),
    (r"cumin|jeera", [("cumin", 1)]),
    (r"spring onion", [("springonion", 1)]),
    (r"\bonions?\b", [("onion", 1)]),
    (r"tomato puree|tomato", [("tomato", 1)]),
    (r"potato", [("potato", 1)]),
    (r"lemon|lime", [("lemon", 1)]),
    (r"\bmint\b", [("mint", 1)]),
    (r"curry leaves", [("curryleaves", 1)]),
    (r"spinach|palak", [("spinach", 1)]),
    (r"cabbage", [("cabbage", 1)]),
    (r"cauliflower|gobi", [("cauliflower", 1)]),
    (r"bhindi|okra", [("bhindi", 1)]),
    (r"mushroom", [("mushrooms", 1)]),
    (r"capsicum", [("capsicum", 1)]),
    (r"green peas|\bpeas\b", [("peas", 1)]),
    (r"cucumber", [("cucumber", 1)]),
    (r"drumstick|pumpkin|brinjal|sambar veg", [("sambarveg", 1)]),
    (r"coconut milk", [("coconutmilk", 1)]),
    (r"coconut oil", [("oil", 1)]),
    (r"coconut", [("coconut", 1)]),
    (r"mixed vegetables|vegetables|beans and carrot|carrot and beans", [("vegmix", 1)]),
    (r"carrot", [("carrot", 1)]),
    (r"\bbeans\b(?!.*rajma)", [("beans", 1)]),
    (r"toor dal", [("toor", 1)]),
    (r"split yellow moong|moong dal", [("moongdal", 1)]),
    (r"whole green moong|sprout", [("wmoong", 1)]),
    (r"urad dal", [("uraddal", 1)]),
    (r"chana dal", [("chanadal", 1)]),
    (r"rajma|kidney bean", [("rajma", 1)]),
    (r"kabuli chana|chickpea", [("kchana", 1)]),
    (r"roasted chana|putani|dalia", [("rchana", 1)]),
    (r"soya", [("soya", 1)]),
    (r"peanut butter", [("peanutbutter", 1)]),
    (r"peanut", [("peanuts", 1)]),
    (r"cashew", [("cashews", 1)]),
    (r"almond|nuts", [("cashews", 1)]),
    (r"makhana", [("makhana", 1)]),
    (r"flaxseed|flax", [("flax", 1)]),
    (r"sesame", [("sesame", 1)]),
    (r"atta|whole-wheat flour|wheat flour|phulkas or parathas", [("atta", 1)]),
    (r"ragi", [("ragi", 1)]),
    (r"poha", [("poha", 1)]),
    (r"\brava\b|semolina", [("rava", 1)]),
    (r"besan|gram flour", [("besan", 1)]),
    (r"rice flour", [("ricefl", 1)]),
    (r"cornflour|corn flour", [("cornflour", 1)]),
    (r"seeraga", [("seeraga", 1)]),
    (r"basmati", [("basmati", 1)]),
    (r"\brice\b", [("rice", 1)]),
    (r"bread", [("bread", 1)]),
    (r"papad", [("papad", 1)]),
    (r"\beggs?\b|egg whites", [("eggs", 1)]),
    (r"coconut milk", [("coconutmilk", 1)]),
    (r"(?<!coconut )\bmilk\b", [("milk", 1)]),
    (r"curd|yogurt|yoghurt", [("curd", 1)]),
    (r"paneer", [("paneer", 1)]),
    (r"\bghee\b", [("ghee", 1)]),
    (r"butter", [("butter", 1)]),
    (r"cream|malai", [("cream", 1)]),
    (r"cheese", [("cheese", 1)]),
    (r"chicken mince|keema|mince", [("mince", 1)]),
    (r"boneless|chicken breast|chicken thigh", [("chickenbl", 1)]),
    (r"chicken", [("chicken", 1)]),
    (r"\bfish\b|seer|pomfret|rohu|basa", [("fish", 1)]),
    (r"prawn|shrimp", [("prawns", 1)]),
    (r"mutton|goat|lamb", [("mutton", 1)]),
    (r"turmeric|haldi", [("turmeric", 1)]),
    (r"biryani masala", [("biryanimasala", 1)]),
    (r"garam masala", [("garam", 1)]),
    (r"chole masala", [("cholemasala", 1)]),
    (r"sambar powder", [("sambarpowder", 1)]),
    (r"bisi bele bath powder", [("bbbpowder", 1)]),
    (r"mustard oil", [("oil", 1)]),
    (r"mustard", [("mustard", 1)]),
    (r"\bhing\b|asafoetida", [("hing", 1)]),
    (r"kasuri methi", [("kasuri", 1)]),
    (r"methi|fenugreek", [("methi_s", 1)]),
    (r"chaat masala", [("chaat", 1)]),
    (r"amchur", [("amchur", 1)]),
    (r"pepper", [("pepper", 1)]),
    (r"fennel|saunf", [("fennel", 1)]),
    (r"ajwain|carom", [("ajwain", 1)]),
    (r"nigella|kalonji", [("cumin", 1)]),
    (r"bay lea|cinnamon|cloves|cardamom|star anise|mace|nutmeg|whole spices|stone flower|kalpasi|marathi mogga",
     [("wholespice", 1)]),
    (r"saffron", [("saffron", 1)]),
    (r"kewra|rose water", [("kewra", 1)]),
    (r"tamarind", [("tamarind", 1)]),
    (r"jaggery", [("jaggery", 1)]),
    (r"sugar", [("sugar", 1)]),
    (r"honey", [("honey", 1)]),
    (r"soy sauce", [("soysauce", 1)]),
    (r"vinegar", [("vinegar", 1)]),
    (r"ketchup", [("ketchup", 1)]),
    (r"chilli sauce|schezwan|sriracha", [("chillisauce", 1)]),
    (r"oregano|mixed herbs|pizza seasoning", [("herbs", 1)]),
    (r"\boil\b", [("oil", 1)]),
    (r"raisin", [("raisins", 1)]),
    (r"\bchill(i|ies)\b", [("greenchilli", 1)]),
    (r"garlic", [("garlic", 1)]),
    (r"ginger", [("ginger", 1)]),
]


def name_keys(name):
    low = name.lower()
    for rx, ks in NAME_RULES:
        if re.search(rx, low):
            return ks
    return None


def add(total, key, g):
    n = NUTR[key]
    for f in FIELDS:
        total[f] = total.get(f, 0) + n[f] * g / 100


def rounded(t):
    out = {}
    for f in FIELDS:
        v = t.get(f, 0)
        out[f] = round(v) if f in ("kcal", "ca", "mg", "k", "na") else round(v, 1)
    return out


COMPOSITE = [  # rows that stand for part of another recipe: grams per batch (1 serving of the master)
    (r"andhra masala and marinade", [("curd", 50), ("ginger", 3.75), ("garlic", 3.75), ("chilli", 1.9),
                                     ("turmeric", .3), ("biryanimasala", 1.9), ("salt", 4), ("lemon", 3.75),
                                     ("greenchilli", 7.5), ("mint", 4), ("oil", 13.5), ("onion", 55),
                                     ("tomato", 50), ("wholespice", 1.5)]),
    (r"andhra marinade", [("curd", 50), ("ginger", 3.75), ("garlic", 3.75), ("chilli", 1.9), ("turmeric", .3),
                          ("biryanimasala", 1.9), ("salt", 3), ("lemon", 3.75), ("greenchilli", 4.5), ("mint", 4)]),
    (r"green masala", [("mint", 15), ("coriander", 15), ("greenchilli", 6), ("ginger", 5), ("garlic", 5),
                       ("wholespice", 1), ("fennel", 1), ("pepper", .5), ("salt", 3)]),
]


def item_grams(name, q):
    low = name.lower()
    for rx, parts in COMPOSITE:
        if re.search(rx, low):
            amt, rest = parse_qty(q)
            return [(k, g * (amt or 1)) for k, g in parts]
    if " / " in q and " / " not in name and name.count(",") == q.count(" / "):
        name = name.replace(", ", " / ")
    """[(key, grams)] for one ingredient row, or None when it can't be read. Handles 'a / b' rows."""
    if " / " in name and " / " in q:
        names, qs = name.split(" / "), q.split(" / ")
        if len(names) == len(qs):
            unit = re.sub(rf"^\s*(?:{NUM}|a pinch|a few)\s*", "", qs[-1])
            out = []
            tail = names[-1].split()[-1]
            for n, qq in zip(names, qs):
                if name_keys(n) is None and name_keys(n + " " + tail) is not None:
                    n = n + " " + tail
                if re.fullmatch(rf"\s*{NUM}\s*", qq) and unit and not re.match(r"[a-z]", n.split()[-1] if False else ""):
                    ks0 = name_keys(n)
                    if ks0 and ks0[0][0] not in EACH:
                        qq = qq + " " + unit
                r = item_grams(n, qq)
                if r is None:
                    return None
                out += r
            return out
    ks = name_keys(name)
    if ks is None:
        return None
    if not ks:
        return []
    parts = re.split(r"\s*\+\s*", q) if "+" in q else [q]
    if "+" in name and len(parts) == 2:  # "Cashews + half the birista"
        a, b = name.split("+", 1)
        ra, rb = item_grams(a, parts[0]), item_grams(b, parts[1])
        return None if ra is None or rb is None else ra + rb
    total = 0.0
    for part in parts:
        g = grams(ks[0][0], part)
        if g is None:
            return None
        total += g
    if ks[0][0] == "salt" and "tbsp" in q:
        total *= 0.1  # salt for boiling water mostly drains away
    if re.search(r"for frying|for deep", name.lower()):
        total *= 0.25  # most frying oil stays in the pan
    return [(k, total * share) for k, share in ks]


SKIP_GROUP = re.compile(r"optional|^to serve|^or ", re.I)


def recipe_total(ingredients):
    """Nutrient totals for a recipe's ingredient groups, plus the rows that couldn't be read."""
    tot, missed = {}, []
    for g in ingredients:
        if SKIP_GROUP.search(g.get("group") or ""):
            continue
        for it in g["items"]:
            if "optional" in (it["name"] + " " + it.get("note", "")).lower():
                continue
            rows = item_grams(it["name"], it.get("q", ""))
            if rows is None:
                missed.append(f'{it["name"]} ({it.get("q", "")})')
                continue
            for k, g_ in rows:
                add(tot, k, g_)
    return tot, missed


def scaled(t, factor):
    return {f: t.get(f, 0) * factor for f in FIELDS}
