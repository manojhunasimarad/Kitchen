# Five-person household planner

The default household has two vegetarians, one eggetarian and two non-vegetarians. Names and
diets are editable in Settings. The kitchen has two cooks, four stove burners, one induction,
one air fryer, a sandwich maker, a fridge, one 3 L pressure cooker and one 5 L pressure cooker.
Mixer availability is unconfirmed: enable it only if available.

## Daily use

1. In Today, choose the date, then open **Who is eating?** for breakfast, lunch and dinner.
2. Select attendees, their portion factors (0.5 / 1 / 1.5 / 2) and eating times.
3. Choose **Suggest for these eaters**, or add dishes manually.
4. Open **Dish recipients** to assign individual dishes. A vegetarian cannot be assigned egg
   or meat; an eggetarian cannot be assigned meat. Non-vegetarians can also eat shared veg/egg.
5. **Cook these portions** opens the recipe with the calculated total servings. The four new
   regional recipes scale method amounts too. Legacy method amounts still need manual scaling.
6. Open ingredient quantities and per-person nutrition. Shopping shows cooking quantities for
   today and tomorrow, omitting finished meals today and dishes with no assigned eaters.

Settings offers either a shared vegetarian meal (fewest separate dishes) or a shared base with
egg and meat additions. In the mixed template, the egg addition initially goes to the eggetarian,
and the chicken addition to the non-vegetarians. Change recipients if someone wants both.
Keep vegetarian utensils and ready-to-eat food separate from raw meat handling.

An example with all five present gives 5 servings of rice, 1 assigned egg portion and 2 meat
portions. If one non-vegetarian is absent, the meat becomes 1 portion and rice becomes 4.
If one vegetarian requests half a portion, rice becomes 3.5. Attendance is independent per meal.

## Cooking-time estimates

Resource allocation uses the configured cooks, burner/induction slots, air fryer, sandwich
maker and the two distinct cookers. A cook remains occupied for a recipe's whole duration,
which is conservative; the planner does not yet have measured hands-on/unattended step times.
It repeats the original base batch for increased portions rather than assuming that a bigger
pan or 5 L cooker can cook any quantity in the same time. Check appliance minimums/fill limits.

Combined session estimates allocate the session's dishes together so a cook or single appliance
is not double-booked. Per-meal estimates also show an estimated start-by time when all attendees
eat together and all recipe durations are known. Different eating times require review of fresh
cooking, refrigeration and reheating; no confident deadline is shown. Fridge presence does not
establish that a particular leftover was handled safely.

Most legacy recipes still have unknown prerequisite times. They can appear as suggestions but
are explicitly flagged **timing needs review**. A suggestion is not a guarantee of meeting the
desired cooking window. In mixed mode additions may exceed the target; the complete workload
must be checked. This is a bounded planner, not a calibrated optimizer or kitchen trial.

## Quantities, nutrition and persistence

Dish servings are the sum of assigned, diet-compatible attendees' portion factors multiplied
by that dish's portion multiplier. Ingredient amounts scale by servings / recipe base yield.
Nutrition is computed per person from their actual assignments, not a shared average. Existing
health targets remain for the selected meter person; five individual clinical profiles are not
implemented. A meal-finished tick applies to the whole meal.

Pantry records currently track presence, not measured grams. Shopping therefore shows total
cooking need and missing ingredient types, not exact quantities remaining to purchase. Recipe
rows remain separate; cross-recipe unit normalization and stock subtraction are future work.
Frying oil is a fixed pan quantity, with a separately disclosed absorbed-oil nutrition assumption.

Attendance, times, assignments and household settings are included in the existing v2 backup.
Older backups remain accepted. Existing menus are preserved, with compatible attendees assumed
present until edited. Member IDs remain stable when names change. Normalization snapshots the
default household settings locally. No personal attendance or names are stored in the repository.

## Recipe source policy

`data/regional_recipes.json` contains original app wording with scoped references and variant
differences, not copied blog articles or pictures. Yennegai uses the Udupi Recipes fresh-coconut
variant; Hebbar's dried-coconut version is compared, not silently combined. Pongal and Kesari
Bath use Dassana's ratios with explicit app portioning. Cabbage pakoda uses a besan-only batter,
not Hebbar's three-flour mixture. Added weights and time ranges need trials in this kitchen.

Run the build, `tools/evaluate.py` and `tools/validation_audit.py` after changing recipes.
The source comparison and engineering checks do not certify taste, safety or measured time.
