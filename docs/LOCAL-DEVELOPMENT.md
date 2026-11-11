# Local cooking companion

This update is local only. It has not been committed, pushed or deployed.

## Start

From the repository folder in PowerShell:

```powershell
.\Start-Local.ps1
```

Or with Python 3.10+:

```sh
python -X utf8 tools/serve.py
```

Open the `http://127.0.0.1:PORT` URL printed in the terminal. The default chooses a free port because some Windows ports are reserved. For a stable URL and persistent browser storage between runs, use `--port 59492` or another available port (`.\Start-Local.ps1 -Port 59492`). Stop with Ctrl+C. A different port is a different browser storage origin; use Settings → Download backup to transfer data. Keep a backup before closing a preview using a random port.

No Python packages, API key, account, or model download are required. The server binds only to loopback and serves only the built website, icons, manifest and worker. It does not serve your repository, backups or environment files.

## What changed

- Pure, tested serving calculations preserve fractions and decimal weights instead of rounding half of a quarter teaspoon to “a little.”
- Pending shopping and store searches no longer count as received pantry stock.
- Ingredient availability is explicitly separate from quantities and completed preparation.
- Saving failures remain visible; backup download and stricter import validation preserve the v2 storage format.
- Recipe links use `#recipe/RECIPE_ID`; serving changes retain meal/day selections and focus.
- Cooking view adds ingredient/method jump buttons, step checkboxes and collapsed nutrition.
- Mobile section selector and larger serving buttons improve navigation.
- Twelve pilot recipes have explicit preparation metadata, component links and review status. All recipes carry honest review status; none is labelled kitchen-tested.
- Time filters use only documented raw-start totals. Unknown prerequisites do not qualify as quick recipes. Times remain source-derived estimates, not calibrated predictions.
- Scoped service-worker cleanup and UTF-8 builds improve local and offline reliability.

## Local retrieval prototype

Open a recipe, then **Local cooking assistant · preview**. Ask a question such as “What needs preparing first?” It retrieves matching method/preparation notes for that recipe using deterministic text search. It displays original snippets, provenance IDs and uncertainty. It does not invent new steps or make unsupported claims about missing amounts. The UI is hidden on public hosts; the GitHub Pages site still works without a backend.

An optional adapter uses an existing local Ollama installation. Install/select a model separately according to your machine's memory and Ollama documentation. This change does not install software or download weights. Start Ollama, then set the exact installed model name:

```powershell
$env:KITCHEN_MODEL = 'YOUR_INSTALLED_MODEL_NAME'
.\Start-Local.ps1
```

The server sends only the typed question and retrieved recipe snippets to `127.0.0.1:11434/api/chat`. It never reads browser health records or pantry data. The model may select evidence IDs or abstain; model-generated recipe prose is deliberately not published by this prototype. Unknown IDs or malformed responses fall back to deterministic search. No cloud inference is configured. This integration has mocked failure/selection tests; a real model was not installed or benchmarked during this update.

This is an initial retrieval workflow, not a fully validated generative cooking assistant. For a public assistant, deploy a separate authenticated/rate-limited service; do not expose this development server to the internet or put secret API keys in frontend code.

## Build and test

```sh
python -X utf8 tools/build_data.py
python -X utf8 tools/build_page.py
python -X utf8 tools/evaluate.py
```

The tests require Node 22+ and Python 3.10+. On this computer, the bundled runtimes can be used if they are not on PATH. `tools/evaluate.py --node PATH_TO_NODE --output report.json` writes machine-readable results. CI runs the same tests and checks generated artifacts are committed. These are engineering tests, not proof of culinary correctness.

## Edit the right source

- `src/template.html`: interface and application behavior.
- `src/core.js`: pure serving, timing, persistence and import helpers, embedded by the builder.
- `data/b2_cards.json`, `data/b1_masters.json`, `tools/world_recipes.py`, `tools/book1_extra.py`: recipe source content.
- `tools/editorial.py`: pilot preparation metadata, limited source references, dependencies and review status.
- `tools/cooking_assistant.py`: deterministic retrieval and optional local-model evidence selection.
- `tools/serve.py`: loopback-only preview/API.
- `tools/audit.py`: historical narrative; **not** an executable test suite.
- `tools/evaluate.py`, `tests/`: executable engineering evaluation.

After editing sources, rebuild `data/data.json`, `index.html` and `sw.js`. Do not edit only generated files. The generated Claude artifact remains in git-ignored `dist/`.

## Still pending

The remaining recipe migration, full ingredient/variant normalization, shopping quantity aggregation, complete safety review, measured appliance/batch scheduling, corpus licensing/ingestion, real-model evaluation and kitchen trials remain future work. Thirteen legacy plain-text ingredient recipes still need manual scaling. The existing health guidance is retained but was not medically reviewed. The site has not been declared accurate merely because code tests pass.

Before pushing, review `git diff` and run the build/tests. Commit the source changes, new tests/docs and generated site together. No push is performed automatically.

## References

- [Ollama local chat API](https://docs.ollama.com/api/chat)
- [FoodSafety.gov temperature guidance](https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures)
- [Dassana's chilla technique](https://www.vegrecipesofindia.com/moong-dal-chilla-recipe/) — a different variant/yield; limited technique corroboration only.

## Household update

See [HOUSEHOLD.md](HOUSEHOLD.md) for attendance, diets, quantities, kitchen capacity and the limits of workload estimates. Regional recipes live in `data/regional_recipes.json`; `tools/regional_recipes.py` validates and compiles them. `src/household.js` contains pure calculations and `src/household-ui.js` the interface, both embedded by the builder.
