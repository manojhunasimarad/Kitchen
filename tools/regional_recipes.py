"""Compile attributed regional adaptations; no claim of kitchen validation."""
import json
import re
from pathlib import Path
from nutrition import add, rounded, scaled

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = re.compile(r"\{\{([a-z0-9-]+)\}\}")


def load_regional(pantry_keys):
    recipes = json.loads((ROOT / 'data/regional_recipes.json').read_text(encoding='utf-8'))
    for r in recipes:
        total, needs, items = {}, [], {}
        for group in r['ingredients']:
            for item in group['items']:
                assert item['id'] not in items, (r['id'], item['id'])
                items[item['id']] = item
                key = item['key']
                assert key in pantry_keys or key in ('salt', 'water'), (r['id'], key)
                if key != 'water':
                    # Frying-oil quantities represent the pan, not measured intake.
                    add(total, key, item.get('nutritionGrams', item['grams']))
                if key not in ('salt', 'water') and not item.get('optional') and key not in needs:
                    needs.append(key)
        def resolve(match):
            assert match[1] in items, (r['id'], match[1])
            return items[match[1]]['q']
        r['steps'] = [REFERENCE.sub(resolve, step) for step in r['stepTemplates']]
        r.update(book=0, page=None, cuisine='Indian', chapter='Regional source-reviewed recipes',
                 diet='veg', oil='', var=[], cues=[], why='', batch=False,
                 needs=needs, strict=list(needs), nutr=rounded(scaled(total, 1 / r['yield'])),
                 serving=r['servingLabel'], minutes=r['timing']['cookMinutes'][1])
        # Source-comparison is not a quick-time or kitchen-tested certificate.
        r['tags'] = ['cooker'] if 'pressure cooker' in r['uses'].lower() else []
    return recipes
