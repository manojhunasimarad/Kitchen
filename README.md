# Kitchen From Zero

A phone-first kitchen planner for a small kitchen with no fridge or oven: two stoves, a pressure cooker, an air fryer and a sandwich maker. It started as a companion to two home cookbooks, *Restaurant-Grade Biryani at Home* (Book 1) and *Everyday Indian Meals at Home* (Book 2), and adds 32 recipes from other cuisines written for the same kitchen.

109 recipes across seven cuisines: Indian, Continental, Italian, Indo-Chinese, Mexican, Middle Eastern and East Asian. Every serving has its nutrition worked out.

![Today on a laptop](docs/screenshots/desktop-today.png)

## What's in it

| Tab | What it does |
| --- | --- |
| **Today** | The day as a kitchen order slip, for any of the next 7 days. Choose whether you cook **once, twice or three times** and for **how many people**. Meals are grouped into cooking sessions, with combined quantities, cooking time, missing items and food-safety notes for a kitchen without a fridge. Add, remove, scale or **shuffle** dishes, or let it plan the whole day. Nutrition for the day is shown against your targets. |
| **Cook** | Tap the ingredients you want to cook with. When one isn't in your pantry, it asks whether to **order it** (opens Swiggy Instamart, Zepto, Blinkit or BigBasket search) or **bring it home**. Dishes from every cuisine that use your picks are listed as ready, one item short or two short. |
| **Surprise me** | Shuffles a random dish that matches your filters: meal, cuisine, diet, only what you can cook now, 30 minutes or less, not cooked yet. Add it to today with one tap. |
| **Recipes** | All 109 recipes, searchable and sortable by protein, iron, calories or time. Each recipe has a **servings** control that rescales the ingredients and nutrition, plus "Add to plan" and the full method. |
| **Pantry** | 108 staples, each marked Have, Low or Out. |
| **Shopping** | Items your plan needs today and tomorrow (with Order and Bring buttons), what you're bringing home, what's on order, and what's running low. *Copy list* puts the list on the clipboard. |
| **Track** | 15 stages and 92 tick-offs, from setting curd to the master biryanis and a World kitchen stage. |
| **Reference** | Daily targets, the five-star scorecard, cooker and air-fryer charts, what keeps without a fridge, food safety, flavour jars and ready-mix masalas. |
| **Settings** | Default people and cooking sessions, your order app, and daily calorie and protein targets. |

<p>
  <img src="docs/screenshots/phone-today.png" width="250" alt="Today, cooking once for two">
  <img src="docs/screenshots/phone-order-or-bring.png" width="250" alt="Order or bring an ingredient">
  <img src="docs/screenshots/phone-surprise.png" width="250" alt="Surprise me">
</p>

## Nutrition

Each recipe's nutrition comes from its ingredient weights. The nutrients are energy, protein, carbs, fat, fibre, iron, calcium, magnesium, zinc, potassium, sodium, vitamin C and vitamin B12. The values per 100 g come from USDA FoodData Central and the Indian Food Composition Tables (IFCT 2017), rounded, in `tools/nutrition.py`. Book recipes have their quantities ("½ tbsp", "1 medium onion", "a pinch") converted to grams by rules in the same file. The new recipes give grams directly. Treat all figures as approximate.

Daily targets: calories and protein are yours to set (defaults 2200 kcal and 110 g). The rest use typical adult-male needs from ICMR-NIN 2020, with sodium as an upper limit.

<img src="docs/screenshots/phone-recipe-nutrition.png" width="300" alt="Nutrition for two servings">

## Using it

**Synced across devices:** published as a Claude artifact, the page saves your plan, ticks, pantry and settings to your Claude account. Open the same link signed in on your phone and laptop and they stay in step.

**Standalone:** open `index.html` in any browser, or turn on GitHub Pages (**Settings → Pages**, deploy from `main`, `/ (root)`). Used this way, everything is saved in that browser only.

"Order" only opens the grocery app's search for the item. You place the order in the app, and the item shows as ordered in Shopping until you tick it as arrived.

## Editing and rebuilding

The page is built from data, so you don't edit `index.html` by hand.

```
src/template.html        layout, styles and app logic (/*DATA*/ is replaced at build time)
data/b2_cards.json       Book 2 recipe cards, extracted from the PDF
data/b1_masters.json     Book 1 master biryanis, extracted from the PDF
data/data.json           the combined app data
tools/world_recipes.py   the 32 recipes from other cuisines (with grams) and quick add-ons like a glass of milk
tools/book1_extra.py     Book 1 variations and sides
tools/nutrition.py       nutrients per 100 g, the gram converter and the ingredient-name rules
tools/build_data.py      pantry, matching rules, cuisine and course, nutrition, track, default week, targets, order apps
tools/build_page.py      embeds data/data.json into the template and writes index.html
tools/extract_b1.py      re-extracts Book 1 from the PDF (needs pdfplumber)
tools/extract_b2.py      re-extracts Book 2 from the PDF (needs pdfplumber)
```

```bash
python3 tools/build_data.py
python3 tools/build_page.py
```

To add a recipe, append an entry to `WORLD` in `tools/world_recipes.py`. Give each ingredient a pantry or nutrition key, a display quantity and its weight in grams, then rebuild.

To re-extract from the books, put the PDFs in `books/` (git-ignored) or pass their paths:

```bash
pip install pdfplumber
python3 tools/extract_b2.py books/Everyday_Indian_Meals_at_Home.pdf
python3 tools/extract_b1.py books/Restaurant_Grade_Biryani_at_Home.pdf
```

## Notes

- Page references (`B1 p. 18`, `B2 p. 37`) point to the PDFs. Protein figures in the app are calculated from ingredients, so they can differ a little from the books.
- The food-safety notes follow the books: without a fridge, eat cooked food within 2 hours, or pack it piping hot into a preheated insulated box. Never keep cooked rice overnight.
- Book 1, page 34: the heading of the five-person party biryani is missing its fraction symbols in the PDF. It should read "two-thirds chicken, one-third paneer".
