"""Recipes from other cuisines, written for the same kitchen: no fridge, no oven, two stoves, a pressure cooker,
an air fryer, a sandwich maker and a mixer. Every quantity is for one serving and carries its weight in grams,
so nutrition is calculated directly.

Ingredient rows: I(nutrition/pantry key, name, display quantity, grams, note, optional)
"""


def I(key, name, q, g, note="", opt=False):
    return {"key": key, "name": name, "q": q, "g": g, "note": note, "opt": opt}


SALT = lambda q="½ tsp", g=3: I("salt", "Salt", q, g)  # noqa: E731

WORLD = [
    # ------------------------------------------------------------------ Continental
    dict(id="lemon-pepper-chicken", title="Lemon-pepper chicken with garlic vegetables", cuisine="Continental",
         course="main", diet="nonveg", time="35 min (15 marinating)", uses="Tawa (air fryer optional)",
         serving="1 plate", keeps="Eat within 2 hours",
         intro="A juicy pan-seared breast with a black-pepper crust and buttery garlic vegetables from the same tawa. "
               "One of the leanest high-protein plates in the app.",
         ing=[("Chicken", [I("chickenbl", "Boneless chicken breast", "180 g", 180, "butterflied or pounded to 1.5 cm"),
                           I("lemon", "Lemon juice", "1 tbsp", 15, "plus a little zest"),
                           I("pepper", "Black pepper, coarsely crushed", "1 tsp", 2.3),
                           I("garlic", "Garlic, grated", "2 cloves", 8), SALT("½ tsp", 3),
                           I("oil", "Oil", "1 tsp", 4.5), I("herbs", "Dried oregano or mixed herbs", "½ tsp", 0.5, opt=True)]),
              ("Vegetables", [I("butter", "Butter", "1 tsp", 4.7), I("garlic", "Garlic, sliced", "1 clove", 4),
                              I("beans", "Beans, cut in 5 cm lengths", "60 g", 60),
                              I("carrot", "Carrot, thin batons", "½", 30),
                              I("capsicum", "Capsicum, strips", "½", 60), SALT("a pinch", 0.5)])],
         steps=["Flatten. Lay the breast between two sheets of plastic and pound it with a rolling pin or a steel "
                "bottle to an even 1.5 cm. Even thickness is what keeps it juicy.",
                "Season. Rub in the salt, pepper, grated garlic, lemon zest, half the lemon juice and the oil. Keep "
                "it covered in the coolest spot for 15 minutes (never more than 2 hours).",
                "Sear. Heat the tawa on medium-high until a drop of water skitters away. Lay the chicken down and "
                "leave it alone for 4–5 minutes, until it lifts off golden. Flip and cook 4–5 minutes more. It is "
                "done when the thickest part is white right through and the juices run clear.",
                "Rest. Move it to a plate for 3 minutes; the juices settle back into the meat.",
                "Vegetables. Lower the heat, add the butter and sliced garlic for 20 seconds, then the beans and "
                "carrot with 2 tbsp water. Cover for 3 minutes, uncover, add the capsicum and toss 2 minutes until "
                "glossy and still crisp. Salt, pepper and the rest of the lemon.",
                "Serve. Slice the chicken against the grain and pour the pan juices over it."],
         tips=[("Air fryer", "Brush with oil and air-fry at 200 °C for 12–14 minutes, turning halfway. Cook the "
                             "vegetables on the tawa meanwhile.")],
         serve="Add 1 phulka or 2 slices of toast if you want carbs."),

    dict(id="chicken-veg-clear-soup", title="Chicken and vegetable clear soup", cuisine="Continental",
         course="soup", diet="nonveg", time="30 min", uses="Pressure cooker", serving="1 big bowl (about 450 ml)",
         keeps="Eat within 2 hours",
         intro="A light dinner for nights you've eaten heavily at lunch. Bone-in chicken gives the broth body without "
               "any cream.",
         ing=[("Soup", [I("chicken", "Bone-in chicken, small pieces", "150 g", 150),
                        I("onion", "Onion, chopped", "½", 50), I("carrot", "Carrot, diced", "½", 40),
                        I("beans", "Beans, chopped", "40 g", 40), I("cabbage", "Cabbage, shredded", "½ cup", 45),
                        I("garlic", "Garlic, crushed", "3 cloves", 12), I("ginger", "Ginger, sliced", "½ inch", 3),
                        I("pepper", "Black pepper, crushed", "½ tsp", 1.2), SALT("¾ tsp", 4.5),
                        I("water", "Water", "500 ml", 0), I("oil", "Oil or butter", "1 tsp", 4.5),
                        I("springonion", "Spring onion, sliced", "1", 15, opt=True),
                        I("lemon", "Lemon juice", "1 tsp", 5)])],
         steps=["Sauté. Heat the oil in the cooker, add garlic and ginger for 30 seconds, then the onion for 2 minutes.",
                "Pressure-cook. Add the chicken, carrot, beans, salt, pepper and 500 ml water. Close and cook "
                "2 whistles on medium; let the pressure drop by itself.",
                "Finish. Open, add the cabbage and simmer 2 minutes. Pull the meat off the bones if you like, taste "
                "for salt and pepper, and add the lemon and spring onion."],
         tips=[("Cloudy or clear", "Keep the lid off and the heat at a bare simmer in the last step; a hard boil "
                                   "makes the broth cloudy.")],
         serve="With 1 slice of toast, or a boiled egg dropped in for +6 g protein."),

    dict(id="tomato-soup-paneer-croutons", title="Tomato soup with air-fried paneer croutons", cuisine="Continental",
         course="soup", diet="veg", time="30 min", uses="Pressure cooker, mixer, air fryer", serving="1 big bowl",
         keeps="Eat within 2 hours",
         intro="Restaurant tomato soup made with milk instead of cream, topped with crisp herby paneer cubes so it "
               "counts as a meal.",
         ing=[("Soup", [I("tomato", "Ripe tomatoes, quartered", "3", 300), I("onion", "Onion, sliced", "½", 50),
                        I("garlic", "Garlic", "2 cloves", 8), I("butter", "Butter", "1 tsp", 4.7),
                        I("sugar", "Sugar", "½ tsp", 2), I("pepper", "Black pepper", "¼ tsp", 0.6),
                        SALT("½ tsp", 3), I("water", "Water", "½ cup", 0), I("milk", "Milk", "¼ cup", 60)]),
              ("Croutons", [I("paneer", "Paneer, 1.5 cm cubes", "75 g", 75), I("oil", "Oil", "½ tsp", 2.3),
                            I("herbs", "Mixed herbs or oregano", "¼ tsp", 0.3),
                            I("chilli", "Chilli flakes or chilli powder", "a pinch", 0.3)])],
         steps=["Cook. Put the tomatoes, onion, garlic, butter, salt and ½ cup water in the cooker; 2 whistles on "
                "medium. Let the pressure drop.",
                "Croutons. Meanwhile toss the paneer with oil, herbs and chilli and air-fry at 200 °C for 7–8 minutes, "
                "shaking once, until golden at the edges.",
                "Blend. Cool the tomatoes 5 minutes, then blend smooth. Strain through a sieve if you want it silky.",
                "Finish. Return to a low flame, stir in the sugar, pepper and milk and heat until steaming; don't "
                "boil hard after the milk goes in. Top with the paneer."],
         tips=[("Deeper flavour", "Char the tomatoes on the tawa for 3–4 minutes before pressure-cooking.")],
         serve="With a slice of toast from the sandwich maker."),

    dict(id="mushroom-cheese-omelette", title="Mushroom and cheese omelette with toast", cuisine="Continental",
         course="breakfast", diet="egg", time="15 min", uses="Tawa, sandwich maker", serving="1 plate",
         keeps="Eat hot",
         intro="A soft folded café omelette, not a masala one. Three eggs and two slices of toast keep you full "
               "until lunch.",
         ing=[("Omelette", [I("eggs", "Eggs", "3", 150), I("mushrooms", "Mushrooms, sliced", "60 g", 60),
                            I("onion", "Onion, finely chopped", "¼", 25), I("capsicum", "Capsicum, finely chopped", "¼", 25),
                            I("butter", "Butter", "1 tsp", 4.7), SALT("¼ tsp", 1.5),
                            I("pepper", "Black pepper", "¼ tsp", 0.6),
                            I("cheese", "Grated cheese", "15 g", 15, opt=True)]),
              ("Toast", [I("bread", "Bread", "2 slices", 56)])],
         steps=["Filling. Melt half the butter on the tawa on medium. Cook the mushrooms without stirring for "
                "2 minutes so they brown, then add onion and capsicum for 1 minute. Salt lightly and tip onto a plate.",
                "Beat. Whisk the eggs with salt and pepper for 30 seconds, until no streaks of white remain.",
                "Cook. Lower the heat, add the rest of the butter and pour in the eggs. As the edges set, push them "
                "to the centre with a spatula and tilt so raw egg runs underneath. Stop while the top is still "
                "slightly wet, about 2 minutes.",
                "Fold. Spoon the filling and cheese over one half, fold, and slide onto the plate. It finishes cooking "
                "in its own heat.",
                "Toast. Toast the bread in the sandwich maker for 2 minutes while the eggs cook."],
         tips=[("Soft, not rubbery", "Low heat and taking it off early is the whole trick.")]),

    dict(id="french-toast-banana", title="French toast with banana", cuisine="Continental", course="breakfast",
         diet="egg", time="12 min", uses="Sandwich maker or tawa", serving="3 slices",
         keeps="Eat hot",
         intro="Sweet breakfast for a change: custardy toast cooked in the sandwich maker with no flipping, "
               "with banana and honey.",
         ing=[("Toast", [I("bread", "Bread (thick slices work best)", "3 slices", 84), I("eggs", "Eggs", "2", 100),
                         I("milk", "Milk", "¼ cup", 60), I("sugar", "Sugar", "1 tsp", 4.2),
                         I("wholespice", "Cinnamon or cardamom powder", "a pinch", 0.3),
                         I("butter", "Butter, for the plates", "1 tsp", 4.7)]),
              ("To serve", [I("banana", "Banana, sliced", "1", 100), I("honey", "Honey", "1 tsp", 7, opt=True)])],
         steps=["Custard. In a wide plate whisk the eggs, milk, sugar and cinnamon.",
                "Soak. Dip each slice for 10 seconds a side so it soaks through but doesn't fall apart.",
                "Cook. Brush the sandwich maker plates with butter, lay in the slices and close for 3–4 minutes, "
                "until golden. On a tawa, cook 2 minutes a side on medium.",
                "Serve. Top with banana and a drizzle of honey."],
         tips=[("More protein", "Add a glass of milk or 2 boiled eggs on the side for +8–12 g.")]),

    dict(id="paneer-steak-garlic-veg", title="Paneer steak with garlic-butter vegetables", cuisine="Continental",
         course="main", diet="veg", time="25 min", uses="Tawa", serving="1 plate", keeps="Eat hot",
         intro="Thick slabs of paneer seared until crusty, with a peppery crust and buttery vegetables. The "
               "vegetarian answer to a steak dinner.",
         ing=[("Paneer", [I("paneer", "Paneer, 2 slabs 1.5 cm thick", "150 g", 150),
                          I("pepper", "Black pepper, crushed", "½ tsp", 1.2),
                          I("herbs", "Mixed herbs or oregano", "½ tsp", 0.5, opt=True),
                          I("chilli", "Chilli flakes or Kashmiri chilli", "¼ tsp", 0.6),
                          I("garlic", "Garlic, grated", "1 clove", 4), SALT("¼ tsp", 1.5),
                          I("oil", "Oil", "1 tsp", 4.5)]),
              ("Vegetables", [I("butter", "Butter", "1 tsp", 4.7), I("garlic", "Garlic, sliced", "2 cloves", 8),
                              I("mushrooms", "Mushrooms, halved", "80 g", 80),
                              I("capsicum", "Capsicum, chunks", "½", 60), I("onion", "Onion, petals", "½", 50),
                              SALT("a pinch", 0.5), I("lemon", "Lemon juice", "1 tsp", 5)])],
         steps=["Season. Pat the paneer dry and rub with salt, pepper, herbs, chilli, garlic and the oil.",
                "Sear. Heat the tawa on medium-high and sear the slabs 2–3 minutes a side, pressing gently, until "
                "deep golden. Move to a plate.",
                "Vegetables. Lower the heat, melt the butter with the sliced garlic, add the mushrooms and leave them "
                "2 minutes to brown, then toss in the onion and capsicum for 2–3 minutes. Salt and lemon.",
                "Serve. Pile the vegetables beside the paneer and pour any butter left on the tawa over the top."],
         tips=[("Soft inside", "Soak the slabs in warm salted water for 10 minutes first if your paneer is firm.")]),

    dict(id="peanut-butter-banana-oats", title="Peanut butter banana oats", cuisine="Continental",
         course="breakfast", diet="veg", time="8 min", uses="1 burner", serving="1 bowl", keeps="Eat hot",
         intro="Hot oats cooked in milk with a spoon of peanut butter: one pot, 8 minutes, about 20 g protein.",
         ing=[("Bowl", [I("oats", "Rolled oats", "½ cup", 45), I("milk", "Milk", "1 cup", 245),
                        I("peanutbutter", "Peanut butter", "1 tbsp", 16), I("banana", "Banana", "1", 100),
                        I("wholespice", "Cinnamon or cardamom powder", "a pinch", 0.3),
                        I("honey", "Honey or jaggery", "1 tsp", 7, opt=True),
                        I("flax", "Flaxseeds, roasted", "1 tsp", 3.5, opt=True), SALT("a pinch", 0.3)])],
         steps=["Cook. Bring the milk to a simmer, add the oats and a pinch of salt, and stir on low for 4–5 minutes "
                "until thick and creamy.",
                "Finish. Off the heat stir in the cinnamon and half the banana, mashed.",
                "Serve. Top with the peanut butter, the rest of the banana sliced, honey and flaxseeds."],
         tips=[("Thicker or thinner", "Add a splash of hot water if it sets too thick in the bowl.")]),

    dict(id="chicken-salad-bowl", title="Chicken salad bowl with mint-curd dressing", cuisine="Continental",
         course="main", diet="nonveg", time="25 min", uses="Air fryer or tawa", serving="1 big bowl",
         keeps="Eat within 2 hours",
         intro="Warm spiced chicken over a crunchy chopped salad with a thick mint and garlic curd dressing. A big "
               "high-protein lunch with very little oil.",
         ing=[("Chicken", [I("chickenbl", "Boneless chicken breast, strips", "150 g", 150),
                           I("kashmiri", "Kashmiri chilli powder", "½ tsp", 1.3),
                           I("pepper", "Black pepper", "½ tsp", 1.2), I("garlic", "Garlic, grated", "1 clove", 4),
                           I("lemon", "Lemon juice", "1 tsp", 5), SALT("¼ tsp", 1.5),
                           I("oil", "Oil", "1 tsp", 4.5)]),
              ("Salad", [I("cucumber", "Cucumber, chunks", "½", 100), I("tomato", "Tomato, chunks", "1 small", 80),
                         I("onion", "Onion, thinly sliced", "¼", 30), I("capsicum", "Capsicum, diced", "¼", 40),
                         I("sweetcorn", "Boiled sweet corn", "¼ cup", 40, opt=True)]),
              ("Dressing", [I("curd", "Thick curd, hung 15 min in a cloth", "¼ cup", 60),
                            I("mint", "Mint leaves, chopped", "2 tbsp", 4), I("garlic", "Garlic, grated", "½ clove", 2),
                            I("lemon", "Lemon juice", "1 tsp", 5), I("cumin_p", "Roasted cumin powder", "¼ tsp", 0.6),
                            SALT("a pinch", 0.5)])],
         steps=["Season. Toss the chicken with chilli, pepper, garlic, lemon, salt and oil; rest 10 minutes.",
                "Cook. Air-fry at 200 °C for 10–12 minutes, shaking once, or sear on a hot tawa 3–4 minutes a side, "
                "until white right through.",
                "Dressing. Stir the hung curd with mint, garlic, lemon, cumin and salt until smooth.",
                "Assemble. Pile the vegetables in a bowl, top with the warm chicken and spoon the dressing over."],
         tips=[("Lunch box", "Pack the dressing separately and eat within 2 hours of cooking the chicken.")]),

    # ------------------------------------------------------------------ Italian
    dict(id="aglio-olio-chicken", title="Spaghetti aglio e olio with chicken", cuisine="Italian", course="main",
         diet="nonveg", time="25 min", uses="2 burners", serving="1 plate", keeps="Eat hot",
         intro="The simplest Italian pasta: garlic gently fried in oil, chilli and pasta water, here with seared "
               "chicken for protein.",
         ing=[("Pasta", [I("pasta", "Spaghetti or any long pasta", "80 g", 80),
                         I("water", "Water for boiling", "1.5 L", 0), I("salt", "Salt for the water", "1 tbsp", 18)]),
              ("Chicken", [I("chickenbl", "Boneless chicken, thin strips", "120 g", 120), SALT("¼ tsp", 1.5),
                           I("pepper", "Black pepper", "¼ tsp", 0.6)]),
              ("Sauce", [I("oil", "Olive oil or any oil", "1½ tbsp", 20),
                         I("garlic", "Garlic, thinly sliced", "6 cloves", 24),
                         I("redchilli", "Chilli flakes", "½ tsp", 0.5),
                         I("herbs", "Dried oregano or parsley", "½ tsp", 0.5, opt=True),
                         I("lemon", "Lemon juice", "1 tsp", 5),
                         I("cheese", "Grated cheese", "1 tbsp", 6, opt=True)])],
         steps=["Boil. Bring 1.5 L water to a rolling boil with 1 tbsp salt. Add the pasta and cook 1 minute less "
                "than the packet says. Keep 1 cup of the pasta water before draining.",
                "Chicken. Meanwhile season the chicken and sear it in 1 tsp of the oil on a hot pan, 2 minutes a side. "
                "Set aside.",
                "Garlic oil. Lower the heat, add the rest of the oil and the garlic. Cook gently 2–3 minutes until "
                "the garlic is pale gold, never brown, then add the chilli flakes for 10 seconds.",
                "Toss. Add the drained pasta, the chicken and ½ cup pasta water. Toss hard over medium heat for "
                "1–2 minutes until the water and oil turn into a glossy sauce that coats the pasta. Add more water "
                "if it looks dry.",
                "Finish. Lemon, herbs, a little cheese, and eat immediately."],
         tips=[("Burnt garlic", "If the garlic browns it turns bitter. Start again; it costs 2 minutes.")]),

    dict(id="penne-arrabbiata-paneer", title="Penne arrabbiata with paneer", cuisine="Italian", course="main",
         diet="veg", time="30 min", uses="2 burners (air fryer optional)", serving="1 plate", keeps="Eat hot",
         intro="'Angry' pasta: a fiery fresh tomato and garlic sauce, with golden paneer cubes stirred through.",
         ing=[("Pasta", [I("pasta", "Penne", "80 g", 80), I("water", "Water for boiling", "1.5 L", 0),
                         I("salt", "Salt for the water", "1 tbsp", 18)]),
              ("Sauce", [I("oil", "Olive oil or any oil", "1 tbsp", 13.5), I("garlic", "Garlic, chopped", "4 cloves", 16),
                         I("redchilli", "Chilli flakes or 2 dried red chillies", "1 tsp", 1),
                         I("tomato", "Ripe tomatoes, finely chopped or grated", "2½", 250),
                         I("sugar", "Sugar", "a pinch", 0.5), SALT("½ tsp", 3),
                         I("herbs", "Dried oregano or basil", "½ tsp", 0.5)]),
              ("Paneer", [I("paneer", "Paneer, 1.5 cm cubes", "100 g", 100), I("oil", "Oil", "½ tsp", 2.3)])],
         steps=["Paneer. Toss the paneer with oil and a pinch of salt and air-fry at 200 °C for 7–8 minutes, or "
                "pan-fry until golden.",
                "Sauce. Heat the oil, add the garlic and chilli for 1 minute on low, then the tomatoes, salt and sugar. "
                "Cook on medium 10–12 minutes, stirring, until thick and the oil shines at the edges.",
                "Pasta. Meanwhile boil the penne in salted water 1 minute short of the packet time; keep ½ cup water.",
                "Toss. Add the pasta, paneer, oregano and a splash of pasta water to the sauce and toss 1 minute."],
         tips=[("Grated tomatoes", "Grate halved tomatoes on a box grater and throw away the skins: smooth sauce, "
                                   "no blender.")]),

    dict(id="white-sauce-pasta-chicken", title="White sauce pasta with chicken and vegetables", cuisine="Italian",
         course="main", diet="nonveg", time="30 min", uses="2 burners", serving="1 plate", keeps="Eat hot",
         intro="Creamy béchamel pasta made with milk, the café favourite, loaded with chicken and vegetables.",
         ing=[("Pasta", [I("pasta", "Penne or fusilli", "80 g", 80), I("water", "Water for boiling", "1.5 L", 0),
                         I("salt", "Salt for the water", "1 tbsp", 18)]),
              ("Chicken and vegetables", [I("chickenbl", "Boneless chicken, small cubes", "100 g", 100),
                                          I("oil", "Oil", "1 tsp", 4.5), I("garlic", "Garlic, chopped", "2 cloves", 8),
                                          I("capsicum", "Capsicum, diced", "¼", 40),
                                          I("mushrooms", "Mushrooms or sweet corn", "40 g", 40),
                                          I("carrot", "Carrot, small dice", "¼", 20)]),
              ("White sauce", [I("butter", "Butter", "1 tbsp", 14), I("atta", "Maida or atta", "1 tbsp", 8),
                               I("milk", "Milk", "1 cup", 245), I("pepper", "Black pepper", "½ tsp", 1.2),
                               I("herbs", "Mixed herbs or oregano", "½ tsp", 0.5), SALT("½ tsp", 3),
                               I("cheese", "Grated cheese", "20 g", 20, opt=True)])],
         steps=["Pasta. Boil the pasta in salted water 1 minute short of the packet time and drain.",
                "Chicken. Sear the chicken in the oil 3–4 minutes, add garlic and the vegetables for 2 minutes, and "
                "set aside.",
                "Roux. In the same pan melt the butter on low, add the flour and stir 1 minute; it should smell like "
                "biscuits, not brown.",
                "Sauce. Pour in the milk a little at a time, whisking, so no lumps form. Simmer 3–4 minutes until it "
                "coats a spoon. Season with salt, pepper and herbs; stir in the cheese.",
                "Combine. Add the pasta, chicken and vegetables and toss 1 minute. Loosen with a splash of milk if thick."],
         tips=[("Lumpy sauce", "Whisk hard off the heat, or pass it through a sieve.")]),

    dict(id="egg-pepper-pasta", title="Egg and pepper pasta (carbonara-style)", cuisine="Italian", course="main",
         diet="egg", time="20 min", uses="2 burners", serving="1 plate", keeps="Eat hot",
         intro="Eggs and cheese turned into a silky sauce by the heat of the pasta, with lots of black pepper. "
               "No cream, no bacon.",
         ing=[("Pasta", [I("pasta", "Spaghetti", "90 g", 90), I("water", "Water for boiling", "1.5 L", 0),
                         I("salt", "Salt for the water", "1 tbsp", 18)]),
              ("Sauce", [I("eggs", "Eggs", "2", 100), I("cheese", "Grated cheese", "25 g", 25),
                         I("pepper", "Black pepper, freshly crushed", "1 tsp", 2.3),
                         I("butter", "Butter", "1 tsp", 4.7), I("garlic", "Garlic, crushed", "2 cloves", 8),
                         I("mushrooms", "Mushrooms, sliced", "50 g", 50, opt=True)])],
         steps=["Mix. Whisk the eggs, cheese and most of the pepper in a bowl.",
                "Boil. Cook the spaghetti in salted water until just done; keep 1 cup pasta water.",
                "Butter. Meanwhile melt the butter with the garlic (and mushrooms, if using) for 2 minutes on low. "
                "Take out the garlic.",
                "Emulsify. Turn the heat off. Add the drained hot pasta to the pan, wait 30 seconds, then pour in the "
                "egg mix with 3 tbsp pasta water and toss quickly. The eggs should turn creamy, not scrambled; add "
                "water a spoon at a time until glossy.",
                "Serve at once with the rest of the pepper."],
         tips=[("Scrambled eggs", "The pan was too hot. Always add the eggs off the heat.")]),

    dict(id="air-fryer-bread-pizza", title="Air-fryer bread pizza (paneer tikka)", cuisine="Italian",
         course="snack", diet="veg", time="20 min", uses="Air fryer", serving="3 slices",
         keeps="Eat hot",
         intro="Crisp bread-base pizzas in 6 minutes: quick tomato sauce, paneer, vegetables and melted cheese.",
         ing=[("Base and sauce", [I("bread", "Bread", "3 slices", 84), I("tomato", "Tomato, grated", "1", 80),
                                  I("ketchup", "Tomato ketchup", "1 tbsp", 15),
                                  I("herbs", "Oregano or pizza seasoning", "½ tsp", 0.5),
                                  I("garlic", "Garlic, grated", "1 clove", 4), SALT("a pinch", 0.5)]),
              ("Toppings", [I("paneer", "Paneer, small cubes", "60 g", 60),
                            I("kashmiri", "Kashmiri chilli powder", "¼ tsp", 0.6), I("curd", "Curd", "1 tbsp", 15),
                            I("capsicum", "Capsicum, diced", "¼", 30), I("onion", "Onion, diced", "¼", 30),
                            I("cheese", "Mozzarella or processed cheese, grated", "40 g", 40),
                            I("butter", "Butter", "½ tsp", 2.3)])],
         steps=["Sauce. Cook the grated tomato, garlic, ketchup, oregano and salt in a small pan for 4–5 minutes "
                "until thick.",
                "Paneer. Toss the paneer with the curd and chilli.",
                "Build. Butter the bread lightly on the underside, spread the sauce on top, then paneer, vegetables "
                "and cheese.",
                "Air-fry. 180 °C for 5–6 minutes, until the cheese bubbles and the edges crisp."],
         tips=[("Chicken pizza", "Use 60 g freshly cooked chicken tikka instead of paneer.")]),

    dict(id="rajma-minestrone", title="Minestrone with rajma", cuisine="Italian", course="soup", diet="veg",
         time="45 min + overnight soak", uses="Pressure cooker", serving="1 big bowl", keeps="Eat within 2 hours",
         intro="A thick Italian vegetable soup with beans and a little pasta: a full one-pot dinner.",
         ing=[("Soup", [I("rajma", "Rajma, soaked overnight and drained", "40 g dry", 40),
                        I("oil", "Olive oil or any oil", "2 tsp", 9), I("onion", "Onion, diced", "½", 50),
                        I("garlic", "Garlic, chopped", "2 cloves", 8), I("carrot", "Carrot, diced", "½", 40),
                        I("beans", "Beans, chopped", "40 g", 40), I("cabbage", "Cabbage, shredded", "½ cup", 45),
                        I("tomato", "Tomatoes, chopped", "1½", 150), I("herbs", "Mixed herbs or oregano", "½ tsp", 0.5),
                        I("pepper", "Black pepper", "¼ tsp", 0.6), SALT("¾ tsp", 4.5),
                        I("water", "Water", "3 cups", 0), I("pasta", "Small pasta or broken spaghetti", "30 g", 30),
                        I("cheese", "Grated cheese", "1 tbsp", 6, opt=True)])],
         steps=["Beans. Pressure-cook the soaked rajma with 1½ cups water: 1 whistle on high, then 20 minutes on the "
                "lowest flame. A bean must mash completely between your fingers.",
                "Base. In a pot, heat the oil and cook onion, garlic and carrot 4 minutes. Add tomatoes and herbs "
                "and cook 5 minutes until soft.",
                "Simmer. Add the rajma with its cooking water, the chopped beans, cabbage, salt, pepper and 1½ cups more water. "
                "Boil, add the pasta and simmer 10 minutes until the pasta is tender.",
                "Finish with pepper and cheese."],
         tips=[("Kabuli chana", "Soaked kabuli chana works the same way and needs the same cooking.")]),

    # ------------------------------------------------------------------ Indo-Chinese
    dict(id="chilli-paneer", title="Chilli paneer (dry)", cuisine="Indo-Chinese", course="main", diet="veg",
         time="25 min", uses="Air fryer, 1 burner", serving="1 plate", keeps="Eat hot",
         intro="Crisp paneer tossed with onion, capsicum and a glossy soy-chilli sauce, with a fraction of the "
               "usual oil because the paneer is air-fried.",
         ing=[("Paneer", [I("paneer", "Paneer, 2 cm cubes", "150 g", 150), I("cornflour", "Cornflour", "1 tbsp", 8),
                          I("soysauce", "Soy sauce", "1 tsp", 5.5), I("pepper", "Black pepper", "¼ tsp", 0.6),
                          I("oil", "Oil spray or brush", "½ tsp", 2.3)]),
              ("Sauce", [I("oil", "Oil", "2 tsp", 9), I("garlic", "Garlic, chopped", "3 cloves", 12),
                         I("ginger", "Ginger, chopped", "½ inch", 3), I("greenchilli", "Green chillies, slit", "2", 6),
                         I("onion", "Onion, 2 cm squares", "½", 70), I("capsicum", "Capsicum, 2 cm squares", "½", 80),
                         I("soysauce", "Soy sauce", "2 tsp", 11), I("chillisauce", "Red chilli sauce", "1 tbsp", 18),
                         I("ketchup", "Tomato ketchup", "1 tsp", 6), I("vinegar", "Vinegar", "1 tsp", 5),
                         I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Coat. Toss the paneer with soy sauce and pepper, then the cornflour until every cube is dusted.",
                "Air-fry. Brush with oil and air-fry at 200 °C for 8–10 minutes, shaking once, until crisp.",
                "Stir-fry. Heat the oil on high. Add garlic, ginger and chillies for 30 seconds, then onion and "
                "capsicum for 2 minutes; they should stay crunchy.",
                "Sauce. Add the soy, chilli sauce, ketchup and vinegar with 2 tbsp water and bubble 30 seconds.",
                "Toss in the paneer and spring onion and serve straight away, before the coating softens."],
         tips=[("Gravy version", "Add ½ cup water mixed with 1 tsp cornflour in the sauce step and simmer until glossy.")]),

    dict(id="chilli-chicken-dry", title="Chilli chicken (air fryer)", cuisine="Indo-Chinese", course="main",
         diet="nonveg", time="35 min (15 marinating)", uses="Air fryer, 1 burner", serving="1 plate",
         keeps="Eat hot",
         intro="Street-style chilli chicken where the chicken is air-fried instead of deep-fried.",
         ing=[("Chicken", [I("chickenbl", "Boneless chicken, bite-size", "175 g", 175),
                           I("ginger", "Ginger-garlic paste", "1 tsp", 5), I("soysauce", "Soy sauce", "1 tsp", 5.5),
                           I("pepper", "Black pepper", "¼ tsp", 0.6), I("kashmiri", "Kashmiri chilli powder", "½ tsp", 1.3),
                           SALT("¼ tsp", 1.5), I("cornflour", "Cornflour", "1 tbsp", 8),
                           I("oil", "Oil spray or brush", "1 tsp", 4.5)]),
              ("Sauce", [I("oil", "Oil", "2 tsp", 9), I("garlic", "Garlic, chopped", "3 cloves", 12),
                         I("greenchilli", "Green chillies, slit", "2", 6), I("onion", "Onion, squares", "½", 70),
                         I("capsicum", "Capsicum, squares", "½", 80), I("soysauce", "Soy sauce", "2 tsp", 11),
                         I("chillisauce", "Red chilli sauce", "1 tbsp", 18), I("vinegar", "Vinegar", "1 tsp", 5),
                         I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Marinate. Mix the chicken with ginger-garlic, soy, pepper, chilli and salt; rest 15 minutes. Toss "
                "with the cornflour just before cooking.",
                "Air-fry. Brush with oil and air-fry at 200 °C for 12–14 minutes, shaking halfway, until crisp and "
                "cooked through.",
                "Stir-fry. Heat the oil on high, add garlic and chillies for 30 seconds, then onion and capsicum for "
                "2 minutes.",
                "Sauce. Add the soy, chilli sauce, vinegar and 2 tbsp water and bubble 30 seconds. Toss the chicken "
                "in and finish with spring onion."],
         tips=[("Ching's sachet", "A Ching's Chilli Chicken sachet can replace the sauces; skip the salt then.")]),

    dict(id="hakka-noodles-egg", title="Veg hakka noodles with egg", cuisine="Indo-Chinese", course="main",
         diet="egg", time="25 min", uses="2 burners", serving="1 plate", keeps="Eat hot",
         intro="Smoky street-style noodles with lots of crunchy vegetables and two eggs scrambled in.",
         ing=[("Noodles", [I("noodles", "Hakka noodles", "80 g", 80), I("water", "Water for boiling", "1 L", 0),
                           I("salt", "Salt for the water", "1 tsp", 6), I("oil", "Oil, to toss", "½ tsp", 2.3)]),
              ("Stir-fry", [I("oil", "Oil", "1 tbsp", 13.5), I("eggs", "Eggs, beaten with a pinch of salt", "2", 100),
                            I("garlic", "Garlic, chopped", "3 cloves", 12), I("onion", "Onion, sliced", "½", 50),
                            I("cabbage", "Cabbage, shredded", "1 cup", 70), I("carrot", "Carrot, thin strips", "½", 40),
                            I("capsicum", "Capsicum, thin strips", "¼", 40), I("soysauce", "Soy sauce", "2 tsp", 11),
                            I("vinegar", "Vinegar", "1 tsp", 5), I("chillisauce", "Chilli sauce", "1 tsp", 6),
                            I("pepper", "Black pepper", "½ tsp", 1.2),
                            I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Boil. Cook the noodles in salted boiling water until just tender (usually 3–4 minutes). Drain, rinse "
                "under the tap to stop them sticking, and toss with ½ tsp oil.",
                "Eggs. Heat 1 tsp oil on high, scramble the eggs into large soft pieces, and tip out.",
                "Vegetables. Add the rest of the oil and get the pan smoking hot. Garlic for 20 seconds, then onion, "
                "cabbage, carrot and capsicum for 2 minutes, tossing constantly.",
                "Toss. Add the noodles, soy sauce, vinegar, chilli sauce and pepper and toss on high for 1–2 minutes. "
                "Fold in the eggs and spring onion."],
         tips=[("Smoky taste", "High heat and a pan that isn't crowded. If your burner is small, cook in two rounds.")]),

    dict(id="chicken-fried-rice", title="Chicken fried rice", cuisine="Indo-Chinese", course="main",
         diet="nonveg", time="30 min (with rice cooked that morning)", uses="2 burners", serving="1 plate",
         keeps="Eat within 2 hours",
         intro="Restaurant fried rice with chicken and egg. Use rice cooked the same day and spread out to cool: "
               "never overnight rice without a fridge.",
         ing=[("Rice", [I("basmati", "Basmati or sona masoori rice, cooked and cooled", "70 g raw", 70)]),
              ("Stir-fry", [I("oil", "Oil", "1 tbsp", 13.5), I("chickenbl", "Boneless chicken, small cubes", "120 g", 120),
                            I("eggs", "Egg", "1", 50), I("garlic", "Garlic, chopped", "3 cloves", 12),
                            I("carrot", "Carrot, small dice", "¼", 30), I("beans", "Beans, chopped", "30 g", 30),
                            I("capsicum", "Capsicum, diced", "¼", 30), I("soysauce", "Soy sauce", "2 tsp", 11),
                            I("vinegar", "Vinegar", "½ tsp", 2.5), I("pepper", "Black pepper", "½ tsp", 1.2),
                            SALT("¼ tsp", 1.5), I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Rice. Cook the rice 1 : 1¾ so it stays firm, spread it on a plate and let it cool and dry for at "
                "least 30 minutes, uncovered.",
                "Chicken. Heat 2 tsp oil on high and stir-fry the chicken with a pinch of salt for 4–5 minutes until "
                "cooked. Push to the side, scramble the egg in the gap, then mix.",
                "Vegetables. Add the rest of the oil, garlic for 20 seconds, then the carrot, beans and capsicum for "
                "2 minutes.",
                "Fry. Add the rice, break up any lumps, and toss on high for 2 minutes. Add soy, vinegar and pepper "
                "and toss 1 minute more. Finish with spring onion."],
         tips=[("Mushy rice", "Rice that is warm and wet steams instead of frying. Cool and dry it well.")]),

    dict(id="soya-manchurian", title="Soya chunk manchurian", cuisine="Indo-Chinese", course="main", diet="veg",
         time="30 min", uses="Air fryer, 1 burner", serving="1 plate", keeps="Eat hot",
         intro="Manchurian made with soya chunks instead of cabbage balls: same sauce, about 25 g protein.",
         ing=[("Soya", [I("soya", "Soya chunks", "40 g", 40), I("water", "Hot salted water, to soak", "2 cups", 0),
                        I("cornflour", "Cornflour", "1 tbsp", 8), I("ricefl", "Rice flour or more cornflour", "1 tsp", 2.6),
                        I("ginger", "Ginger-garlic paste", "1 tsp", 5), I("kashmiri", "Kashmiri chilli powder", "½ tsp", 1.3),
                        I("soysauce", "Soy sauce", "1 tsp", 5.5), I("oil", "Oil spray or brush", "1 tsp", 4.5)]),
              ("Sauce", [I("oil", "Oil", "2 tsp", 9), I("garlic", "Garlic, chopped", "3 cloves", 12),
                         I("greenchilli", "Green chillies, chopped", "2", 6), I("onion", "Onion, diced", "½", 60),
                         I("capsicum", "Capsicum, diced", "¼", 40), I("soysauce", "Soy sauce", "2 tsp", 11),
                         I("chillisauce", "Chilli sauce", "2 tsp", 12), I("ketchup", "Ketchup", "1 tsp", 6),
                         I("vinegar", "Vinegar", "1 tsp", 5), I("cornflour", "Cornflour in ⅓ cup water", "1 tsp", 2.7),
                         I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Soak. Soak the soya chunks in hot salted water for 10 minutes. Squeeze them hard, twice; dry chunks "
                "crisp, wet ones don't.",
                "Coat. Toss with ginger-garlic, chilli, soy, then the cornflour and rice flour.",
                "Air-fry. Brush with oil and air-fry at 200 °C for 10–12 minutes, shaking once, until crisp.",
                "Sauce. Heat the oil, fry garlic and chillies 30 seconds, add onion and capsicum for 2 minutes, then "
                "soy, chilli sauce, ketchup and vinegar. Stir in the cornflour water and simmer until glossy, "
                "about 1 minute.",
                "Toss the soya in, finish with spring onion and serve hot."],
         tips=[("Gobi manchurian", "Use 200 g cauliflower florets instead; air-fry 15 minutes.")]),

    dict(id="hot-sour-chicken-soup", title="Hot and sour chicken soup", cuisine="Indo-Chinese", course="soup",
         diet="nonveg", time="25 min", uses="1 burner", serving="1 big bowl", keeps="Eat hot",
         intro="Peppery, tangy and thick, with shredded chicken and ribbons of egg: a filling dinner in a bowl.",
         ing=[("Soup", [I("oil", "Oil", "1 tsp", 4.5), I("garlic", "Garlic, chopped", "3 cloves", 12),
                        I("ginger", "Ginger, chopped", "½ inch", 3), I("greenchilli", "Green chilli, chopped", "1", 3),
                        I("chickenbl", "Boneless chicken, finely shredded", "100 g", 100),
                        I("cabbage", "Cabbage, shredded", "¼ cup", 25), I("carrot", "Carrot, thin strips", "¼", 30),
                        I("mushrooms", "Mushrooms, sliced", "30 g", 30), I("water", "Water", "1¾ cups", 0),
                        I("soysauce", "Soy sauce", "1 tbsp", 16), I("vinegar", "Vinegar", "1 tbsp", 15),
                        I("chillisauce", "Chilli sauce", "1 tsp", 6), I("pepper", "Black pepper", "½ tsp", 1.2),
                        I("cornflour", "Cornflour in 3 tbsp water", "1 tbsp", 8),
                        I("eggs", "Egg, beaten", "1", 50), I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Base. Heat the oil and fry garlic, ginger and chilli for 30 seconds. Add the chicken and stir until "
                "it turns white, 2 minutes.",
                "Simmer. Add the vegetables and water, bring to a boil and simmer 5 minutes.",
                "Season. Stir in soy, vinegar, chilli sauce and pepper. Pour in the cornflour slurry while stirring "
                "and simmer 1 minute until thick.",
                "Egg ribbons. Turn the heat to low and pour the egg in a thin stream while stirring slowly in one "
                "direction. Off the heat; add spring onion. Taste: it should be sharp and peppery."],
         tips=[("Veg version", "Use 100 g paneer, finely diced, or extra mushrooms instead of chicken.")]),

    # ------------------------------------------------------------------ Mexican
    dict(id="rajma-burrito-bowl", title="Rajma burrito bowl", cuisine="Mexican", course="main", diet="veg",
         time="50 min + overnight soak", uses="Pressure cooker, 1 burner", serving="1 big bowl",
         keeps="Eat within 2 hours",
         intro="Cumin-spiced beans, rice, fresh tomato salsa and a cool curd 'sour cream': a burrito without the "
               "wrap.",
         ing=[("Beans", [I("rajma", "Rajma, soaked overnight", "50 g dry", 50), I("oil", "Oil", "1 tsp", 4.5),
                         I("onion", "Onion, chopped", "¼", 30), I("garlic", "Garlic, chopped", "2 cloves", 8),
                         I("kashmiri", "Kashmiri chilli powder", "1 tsp", 2.5),
                         I("cumin_p", "Roasted cumin powder", "½ tsp", 1.3), SALT("½ tsp", 3)]),
              ("Rice", [I("rice", "Rice", "60 g", 60), I("lemon", "Lemon juice", "1 tsp", 5),
                        I("coriander", "Coriander, chopped", "1 tbsp", 1.2)]),
              ("Salsa and toppings", [I("tomato", "Tomato, finely diced", "1", 100), I("onion", "Onion, finely diced", "¼", 30),
                                      I("greenchilli", "Green chilli, chopped", "½", 1.5),
                                      I("lemon", "Lemon juice", "1 tsp", 5), I("coriander", "Coriander", "1 tbsp", 1.2),
                                      I("capsicum", "Capsicum, diced and seared", "¼", 40),
                                      I("sweetcorn", "Boiled sweet corn", "¼ cup", 40, opt=True),
                                      I("curd", "Thick curd, hung", "¼ cup", 60), SALT("a pinch", 0.5),
                                      I("cheese", "Grated cheese", "15 g", 15, opt=True)])],
         steps=["Beans. Pressure-cook the soaked rajma with 1 cup water: 1 whistle on high, then 20 minutes on the "
                "lowest flame, until a bean mashes completely.",
                "Rice. Cook the rice; stir in lemon and coriander.",
                "Season the beans. Heat the oil, cook onion and garlic 3 minutes, add chilli, cumin and salt for "
                "20 seconds, then the beans with a little of their liquid. Simmer 5 minutes, mashing a few beans to "
                "thicken.",
                "Salsa. Mix tomato, onion, chilli, lemon, coriander and a pinch of salt.",
                "Bowl. Rice, beans, salsa, seared capsicum and corn, with a spoon of hung curd and the cheese."],
         tips=[("Sour cream", "Hang the curd in a cloth for 15 minutes and stir in a pinch of salt and lemon.")]),

    dict(id="chicken-quesadilla", title="Chicken quesadilla in the sandwich maker", cuisine="Mexican",
         course="main", diet="nonveg", time="30 min", uses="Sandwich maker, 1 burner", serving="2 quesadillas",
         keeps="Eat hot",
         intro="Spiced chicken, peppers and melted cheese sealed between two thin rotis or wraps and pressed in the "
               "sandwich maker.",
         ing=[("Filling", [I("chickenbl", "Boneless chicken, small pieces", "120 g", 120), I("oil", "Oil", "1 tsp", 4.5),
                           I("onion", "Onion, sliced", "¼", 30), I("capsicum", "Capsicum, sliced", "¼", 40),
                           I("garlic", "Garlic, chopped", "1 clove", 4), I("kashmiri", "Kashmiri chilli powder", "1 tsp", 2.5),
                           I("cumin_p", "Roasted cumin powder", "½ tsp", 1.3),
                           I("herbs", "Oregano", "¼ tsp", 0.3, opt=True), SALT("¼ tsp", 1.5),
                           I("lemon", "Lemon juice", "1 tsp", 5)]),
              ("To assemble", [I("atta", "Atta, for 4 thin rotis (or 2 large wheat wraps)", "70 g", 70),
                               I("cheese", "Grated cheese", "30 g", 30), I("tomato", "Tomato, diced", "½", 40),
                               I("butter", "Butter, for the plates", "½ tsp", 2.3)])],
         steps=["Rotis. Knead the atta with water and a pinch of salt and roll 4 thin rotis the size of the sandwich "
                "plates. Cook them 20 seconds a side on the tawa, just until set (or use wraps).",
                "Filling. Heat the oil on high and cook the chicken 4 minutes, add onion, capsicum and garlic for "
                "2 minutes, then the spices, salt and lemon. It should be dry, not saucy.",
                "Build. Roti, half the cheese, half the filling and tomato, another roti.",
                "Press. Brush the plates with butter and toast 3–4 minutes until golden and the cheese melts. "
                "Repeat for the second."],
         tips=[("Paneer quesadilla", "Use 120 g crumbled paneer instead of chicken; cook the filling only 2 minutes.")]),

    dict(id="egg-breakfast-burrito", title="Egg breakfast burrito", cuisine="Mexican", course="breakfast",
         diet="egg", time="20 min", uses="1 burner", serving="2 wraps", keeps="Eat hot",
         intro="Soft-scrambled eggs, peppers, salsa and cheese rolled in rotis: a hand-held breakfast with "
               "about 30 g protein.",
         ing=[("Wraps", [I("atta", "Atta, for 2 rotis (or 2 wheat wraps)", "60 g", 60)]),
              ("Filling", [I("eggs", "Eggs", "3", 150), I("butter", "Butter or oil", "1 tsp", 4.7),
                           I("onion", "Onion, chopped", "¼", 30), I("capsicum", "Capsicum, chopped", "¼", 30),
                           I("tomato", "Tomato, diced", "½", 50), I("kashmiri", "Kashmiri chilli powder", "½ tsp", 1.3),
                           I("cumin_p", "Roasted cumin powder", "¼ tsp", 0.6), SALT("¼ tsp", 1.5),
                           I("coriander", "Coriander", "1 tbsp", 1.2),
                           I("cheese", "Grated cheese", "15 g", 15, opt=True),
                           I("chillisauce", "Chilli sauce or green chutney", "1 tsp", 6, opt=True)])],
         steps=["Rotis. Make 2 rotis or warm the wraps on the tawa.",
                "Vegetables. Melt the butter, cook onion and capsicum 2 minutes, add the spices for 10 seconds.",
                "Eggs. Beat the eggs with salt, pour into the pan on low and stir slowly until just set and creamy. "
                "Add the tomato and coriander.",
                "Roll. Spoon onto the rotis, add cheese and sauce, fold in the sides and roll tight. Toast "
                "seam-side down for 30 seconds to seal."]),

    # ------------------------------------------------------------------ Middle Eastern
    dict(id="hummus", title="Hummus", cuisine="Middle Eastern", course="side", diet="veg",
         time="40 min + overnight soak", uses="Pressure cooker, mixer", serving="2 servings as a dip", yield_=2,
         keeps="Eat the same day",
         intro="Smooth chickpea and sesame dip. Eat it with phulka, cucumber and carrot sticks, or alongside "
               "air-fryer chicken.",
         ing=[("Hummus", [I("kchana", "Kabuli chana, soaked overnight", "50 g dry", 50),
                          I("sesame", "White sesame seeds, toasted", "1 tbsp", 9),
                          I("oil", "Olive oil or any mild oil", "1 tbsp", 13.5), I("garlic", "Garlic", "1 clove", 4),
                          I("lemon", "Lemon juice", "1½ tbsp", 22), I("cumin_p", "Roasted cumin powder", "¼ tsp", 0.6),
                          SALT("½ tsp", 3), I("water", "Ice-cold water", "3–4 tbsp", 0),
                          I("kashmiri", "Kashmiri chilli, to sprinkle", "a pinch", 0.3)])],
         steps=["Cook. Pressure-cook the soaked chana with a pinch of salt and 1½ cups water: 1 whistle on high, "
                "then 15–20 minutes on the lowest flame, until very soft. Drain and cool 10 minutes.",
                "Tahini. Grind the toasted sesame with half the oil to a paste.",
                "Blend. Add the chana, garlic, lemon, cumin and salt and blend, adding ice-cold water a spoon at a "
                "time, until very smooth and light, 2–3 minutes.",
                "Serve. Spread in a bowl, make a swirl, pour over the rest of the oil and sprinkle with chilli."],
         tips=[("Extra smooth", "Pinch the skins off the cooked chickpeas before blending.")]),

    dict(id="chicken-shawarma-wrap", title="Air-fryer chicken shawarma wrap", cuisine="Middle Eastern",
         course="main", diet="nonveg", time="40 min (20 marinating)", uses="Air fryer, 1 burner",
         serving="2 wraps", keeps="Eat within 2 hours",
         intro="Spiced chicken thigh, garlic curd sauce and crunchy vegetables rolled tight. Close to the street "
               "version, with about 45 g protein.",
         ing=[("Chicken", [I("chickenbl", "Boneless chicken thigh, strips", "150 g", 150), I("curd", "Curd", "2 tbsp", 30),
                           I("kashmiri", "Kashmiri chilli powder", "1 tsp", 2.5),
                           I("cumin_p", "Roasted cumin powder", "½ tsp", 1.3),
                           I("coriander_p", "Coriander powder", "½ tsp", 1.3), I("pepper", "Black pepper", "¼ tsp", 0.6),
                           I("turmeric", "Turmeric", "a pinch", 0.3), I("wholespice", "Cinnamon powder", "a pinch", 0.3),
                           I("garlic", "Garlic, grated", "2 cloves", 8), I("lemon", "Lemon juice", "1 tsp", 5),
                           I("oil", "Oil", "1 tsp", 4.5), SALT("½ tsp", 3)]),
              ("Garlic sauce", [I("curd", "Thick curd, hung 15 min", "¼ cup", 60), I("garlic", "Garlic, grated", "1 clove", 4),
                                I("lemon", "Lemon juice", "1 tsp", 5), I("oil", "Oil", "1 tsp", 4.5),
                                SALT("a pinch", 0.5)]),
              ("Wrap", [I("atta", "Atta, for 2 thin rotis (or 2 wraps)", "70 g", 70),
                        I("onion", "Onion, thinly sliced", "¼", 30), I("cucumber", "Cucumber, sticks", "¼", 50),
                        I("tomato", "Tomato, sliced", "½", 50), I("cabbage", "Cabbage, shredded", "¼ cup", 25)])],
         steps=["Marinate. Mix the chicken with everything in the chicken list; 20 minutes covered (up to 2 hours).",
                "Air-fry. 200 °C for 12–14 minutes, shaking halfway, until charred at the edges.",
                "Sauce. Stir the hung curd with garlic, lemon, oil and salt until smooth.",
                "Wrap. Make 2 thin rotis. Spread sauce, add chicken and vegetables, roll tight and toast seam-side "
                "down on the tawa or in the sandwich maker for 1 minute."],
         tips=[("Paneer shawarma", "Use 150 g paneer strips; air-fry 8–10 minutes.")]),

    dict(id="air-fryer-falafel", title="Air-fryer falafel with garlic curd", cuisine="Middle Eastern",
         course="snack", diet="veg", time="35 min + overnight soak", uses="Mixer, air fryer", serving="8 small falafel",
         keeps="Eat hot",
         intro="Herby chickpea patties made from soaked (not cooked) chana and air-fried crisp.",
         ing=[("Falafel", [I("kchana", "Kabuli chana, soaked 10–12 hours, drained", "60 g dry", 60),
                           I("onion", "Onion, chopped", "¼", 30), I("garlic", "Garlic", "2 cloves", 8),
                           I("coriander", "Coriander leaves", "½ cup", 8), I("mint", "Mint leaves", "2 tbsp", 4),
                           I("greenchilli", "Green chilli", "1", 3), I("cumin_p", "Roasted cumin powder", "1 tsp", 2.5),
                           I("coriander_p", "Coriander powder", "1 tsp", 2.5), I("besan", "Besan", "1 tbsp", 7),
                           SALT("½ tsp", 3), I("oil", "Oil, to brush", "2 tsp", 9)]),
              ("Garlic curd", [I("curd", "Thick curd", "⅓ cup", 80), I("garlic", "Garlic, grated", "½ clove", 2),
                               I("lemon", "Lemon juice", "1 tsp", 5), SALT("a pinch", 0.5)])],
         steps=["Grind. Pulse the soaked raw chana with onion, garlic, herbs, chilli, spices and salt to a coarse, "
                "damp crumb, like couscous. Don't make a paste.",
                "Shape. Mix in the besan, then press into 8 small patties. If they crumble, pulse 2 seconds more.",
                "Air-fry. Brush with oil and air-fry at 190 °C for 14–16 minutes, turning halfway, until deep golden.",
                "Serve with the garlic curd, cucumber and tomato, or tucked into a phulka."],
         tips=[("Never cooked chana", "Cooked chickpeas make falafel fall apart; they must be soaked raw.")]),

    dict(id="shakshuka", title="Shakshuka (eggs in spiced tomato)", cuisine="Middle Eastern", course="breakfast",
         diet="egg", time="25 min", uses="1 burner", serving="1 pan", keeps="Eat hot",
         intro="Eggs poached in a smoky pepper and tomato sauce. Mop it up with toast or phulka; it works for "
               "dinner too.",
         ing=[("Sauce", [I("oil", "Oil", "1 tbsp", 13.5), I("cumin", "Cumin seeds", "½ tsp", 1),
                         I("onion", "Onion, sliced", "½", 70), I("capsicum", "Capsicum, sliced", "½", 70),
                         I("garlic", "Garlic, sliced", "2 cloves", 8),
                         I("kashmiri", "Kashmiri chilli powder", "1 tsp", 2.5), I("pepper", "Black pepper", "¼ tsp", 0.6),
                         I("tomato", "Tomatoes, chopped", "2½", 250), SALT("½ tsp", 3)]),
              ("Eggs", [I("eggs", "Eggs", "3", 150), I("coriander", "Coriander", "1 tbsp", 1.2),
                        I("bread", "Bread or 1 phulka, to serve", "2 slices", 56)])],
         steps=["Sauce. Heat the oil, crackle the cumin, then cook onion and capsicum 5 minutes until soft. Add "
                "garlic and chilli for 30 seconds, then the tomatoes and salt. Simmer 8–10 minutes until thick.",
                "Eggs. Make 3 wells with a spoon and crack an egg into each. Cover and cook on low for 5–7 minutes, "
                "until the whites are set and the yolks still soft (longer for firm yolks).",
                "Serve from the pan with coriander, pepper and toast."]),

    # ------------------------------------------------------------------ East Asian
    dict(id="thai-red-curry-chicken", title="Thai red curry with chicken and rice", cuisine="East Asian",
         course="main", diet="nonveg", time="30 min", uses="2 burners", serving="1 plate", keeps="Eat hot",
         intro="Coconut milk curry from a ready red curry paste, with vegetables and tulsi (holy basil, the herb "
               "Thai cooks use).",
         ing=[("Curry", [I("oil", "Oil", "1 tsp", 4.5), I("currypaste", "Thai red curry paste", "1 tbsp", 15),
                         I("chickenbl", "Boneless chicken, thin slices", "150 g", 150),
                         I("coconutmilk", "Coconut milk", "½ cup", 120), I("water", "Water", "¼ cup", 0),
                         I("capsicum", "Capsicum, strips", "½", 60), I("beans", "Beans, cut", "40 g", 40),
                         I("onion", "Onion, wedges", "¼", 40), I("jaggery", "Jaggery or sugar", "½ tsp", 2.5),
                         I("soysauce", "Soy sauce", "1 tsp", 5.5), I("lemon", "Lemon juice", "1 tsp", 5),
                         I("tulsi", "Tulsi (holy basil) leaves", "10", 2)]),
              ("Rice", [I("rice", "Rice", "70 g", 70)])],
         steps=["Rice. Start the rice.",
                "Paste. Heat the oil and fry the curry paste on low for 1 minute, until it smells fragrant.",
                "Chicken. Add the chicken and stir 2 minutes to coat. Pour in the coconut milk and water and bring to "
                "a gentle simmer (a hard boil splits coconut milk).",
                "Vegetables. Add onion, beans and capsicum and simmer 5–6 minutes until the chicken is cooked and the "
                "beans tender-crisp.",
                "Balance. Season with jaggery, soy and lemon: it should be spicy, slightly sweet and salty. Tear in "
                "the tulsi and serve over rice."],
         tips=[("Opened paste and coconut milk", "Without a fridge, buy single-use sachets and small tetra packs.")]),

    dict(id="teriyaki-chicken-bowl", title="Teriyaki chicken rice bowl", cuisine="East Asian", course="main",
         diet="nonveg", time="30 min", uses="2 burners", serving="1 bowl", keeps="Eat hot",
         intro="Glossy soy, honey, ginger and garlic glazed chicken over rice with a quick cucumber salad.",
         ing=[("Chicken", [I("chickenbl", "Boneless chicken thigh or breast", "150 g", 150), I("oil", "Oil", "1 tsp", 4.5),
                           I("soysauce", "Soy sauce", "1 tbsp", 16), I("honey", "Honey", "1 tbsp", 21),
                           I("ginger", "Ginger, grated", "½ inch", 3), I("garlic", "Garlic, grated", "2 cloves", 8),
                           I("vinegar", "Vinegar", "1 tsp", 5), I("cornflour", "Cornflour in 3 tbsp water", "1 tsp", 2.7),
                           I("sesame", "Sesame seeds, toasted", "1 tsp", 3, opt=True)]),
              ("Bowl", [I("rice", "Rice", "70 g", 70), I("cucumber", "Cucumber, thin slices", "½", 80),
                        I("vinegar", "Vinegar", "1 tsp", 5), I("sugar", "Sugar", "a pinch", 0.5),
                        SALT("a pinch", 0.5), I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Rice. Cook the rice. Toss the cucumber with vinegar, sugar and salt and set aside.",
                "Sauce. Stir together soy, honey, ginger, garlic, vinegar and the cornflour water.",
                "Sear. Heat the oil on medium-high and cook the chicken 4–5 minutes a side until golden and cooked "
                "through. Slice it.",
                "Glaze. Pour the sauce into the pan and bubble 1 minute until syrupy. Add the chicken and turn to coat.",
                "Bowl. Rice, chicken, cucumber, sesame and spring onion."]),

    dict(id="peanut-sesame-noodles", title="Peanut sesame noodles with egg", cuisine="East Asian", course="main",
         diet="egg", time="20 min", uses="2 burners", serving="1 bowl", keeps="Eat within 2 hours",
         intro="Noodles in a creamy peanut-butter, soy and chilli sauce with crunchy vegetables and two eggs.",
         ing=[("Noodles", [I("noodles", "Noodles", "80 g", 80), I("water", "Water for boiling", "1 L", 0)]),
              ("Sauce", [I("peanutbutter", "Peanut butter", "1½ tbsp", 24), I("soysauce", "Soy sauce", "2 tsp", 11),
                         I("vinegar", "Vinegar", "1 tsp", 5), I("honey", "Honey or jaggery", "1 tsp", 7),
                         I("garlic", "Garlic, grated", "1 clove", 4), I("ginger", "Ginger, grated", "¼ inch", 2),
                         I("chillisauce", "Chilli sauce or chilli flakes", "1 tsp", 6),
                         I("water", "Hot noodle water", "3 tbsp", 0)]),
              ("Toppings", [I("eggs", "Eggs, boiled (air fryer) or fried", "2", 100),
                            I("cucumber", "Cucumber, thin sticks", "¼", 60), I("carrot", "Carrot, thin sticks", "½", 40),
                            I("sesame", "Sesame seeds", "1 tsp", 3, opt=True),
                            I("springonion", "Spring onion", "1", 15, opt=True)])],
         steps=["Eggs. Air-fry the eggs at 130 °C for 13 minutes (jammy) or fry them.",
                "Sauce. In a big bowl whisk the peanut butter, soy, vinegar, honey, garlic, ginger and chilli sauce.",
                "Noodles. Boil the noodles until just tender. Whisk 3 tbsp of the hot water into the sauce, then "
                "drain the noodles and toss them in the bowl until coated.",
                "Top with the vegetables, halved eggs, sesame and spring onion."]),

    dict(id="korean-egg-rice-bowl", title="Korean egg rice bowl (gyeran bap)", cuisine="East Asian",
         course="breakfast", diet="egg", time="10 min (with cooked rice)", uses="1 burner", serving="1 bowl",
         keeps="Eat hot",
         intro="Hot rice, crisp-edged fried eggs, butter, soy and sesame: Korea's 10-minute comfort food. Great "
               "for lunch when the rice is already cooked.",
         ing=[("Bowl", [I("rice", "Rice, freshly cooked", "80 g raw", 80), I("eggs", "Eggs", "2", 100),
                        I("butter", "Butter", "1 tsp", 4.7), I("soysauce", "Soy sauce", "2 tsp", 11),
                        I("sesame", "Sesame seeds, toasted", "1 tsp", 3), I("springonion", "Spring onion", "1", 15),
                        I("chillisauce", "Chilli sauce", "1 tsp", 6, opt=True),
                        I("cucumber", "Cucumber, sliced, with a splash of vinegar", "¼", 50),
                        I("vinegar", "Vinegar", "½ tsp", 2.5)])],
         steps=["Eggs. Heat a little of the butter on medium-high and fry the eggs until the edges are crisp and lacy "
                "and the yolks still runny, about 2 minutes.",
                "Bowl. Put hot rice in a bowl with the rest of the butter, lay the eggs on top and drizzle the soy.",
                "Finish with sesame, spring onion and chilli sauce, with the cucumber on the side. Break the yolks and "
                "mix everything together."]),

    dict(id="thai-basil-chicken", title="Thai basil chicken (pad kra pao)", cuisine="East Asian", course="main",
         diet="nonveg", time="20 min", uses="2 burners", serving="1 plate", keeps="Eat hot",
         intro="Fiery stir-fried chicken mince with garlic, chillies and tulsi (holy basil), with rice and a "
               "crisp fried egg. One of Thailand's favourite quick lunches.",
         ing=[("Stir-fry", [I("oil", "Oil", "2 tsp", 9), I("garlic", "Garlic, crushed", "4 cloves", 16),
                            I("greenchilli", "Green chillies, crushed", "3", 9),
                            I("mince", "Chicken mince", "150 g", 150), I("onion", "Onion, sliced", "¼", 40),
                            I("capsicum", "Capsicum, sliced", "¼", 40, opt=True),
                            I("soysauce", "Soy sauce", "2 tsp", 11), I("jaggery", "Jaggery or sugar", "1 tsp", 5),
                            I("tulsi", "Tulsi (holy basil) leaves", "a handful", 8)]),
              ("To serve", [I("rice", "Rice", "70 g", 70), I("eggs", "Egg, fried", "1", 50),
                            I("oil", "Oil, for the egg", "1 tsp", 4.5)])],
         steps=["Rice. Cook the rice.",
                "Aromatics. Heat the oil on high, add garlic and chillies and stir 20 seconds.",
                "Chicken. Add the mince and break it up; cook 4–5 minutes until no pink remains and it starts to "
                "brown. Add onion and capsicum for 1 minute.",
                "Season. Add soy, jaggery and 2 tbsp water and toss until glossy. Off the heat, stir in the tulsi "
                "until it wilts.",
                "Egg. Fry the egg in hot oil until crisp at the edges and serve on the rice with the chicken."],
         tips=[("Paneer kra pao", "Use 150 g crumbled paneer; add it after the onion and cook 2 minutes.")]),
]

# quick add-ons for the day plan, so a glass of milk or a bowl of curd counts toward the day
EXTRAS = [
    {"id": "x-milk", "title": "Glass of milk (250 ml)", "items": [("milk", 250)]},
    {"id": "x-curd", "title": "Bowl of curd (150 g)", "items": [("curd", 150)]},
    {"id": "x-banana", "title": "Banana", "items": [("banana", 100)]},
    {"id": "x-eggs", "title": "2 boiled eggs", "items": [("eggs", 100)]},
    {"id": "x-peanuts", "title": "Roasted peanuts (30 g)", "items": [("peanuts", 30)]},
    {"id": "x-chana", "title": "Roasted chana (30 g)", "items": [("rchana", 30)]},
    {"id": "x-pbtoast", "title": "Peanut butter toast (2 slices)", "items": [("bread", 56), ("peanutbutter", 16)]},
    {"id": "x-phulka", "title": "2 phulkas", "items": [("atta", 60)]},
    {"id": "x-rice", "title": "Bowl of rice (60 g raw)", "items": [("rice", 60)]},
]
