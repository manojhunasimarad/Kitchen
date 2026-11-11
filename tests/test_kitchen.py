import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from cooking_assistant import answer, retrieve
from editorial import PILOT

class RecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'data/data.json').read_text(encoding='utf-8'))
        cls.recipes={r['id']:r for r in cls.data['recipes']}
    def test_structural_contract(self):
        self.assertEqual(len(self.recipes),113)
        pantry={p['key'] for p in self.data['pantry']}
        for r in self.recipes.values():
            self.assertTrue(r['steps']);self.assertTrue(r['ingredients']);self.assertGreater(r['yield'],0)
            self.assertFalse(r['review']['kitchenTested'])
            for t in r['needs']+r['strict']: self.assertTrue(set(t.split('|'))<=pantry)
            for d in r['dependencies']: self.assertIn(d,self.recipes)
            self.assertEqual(len(r['steps']),len(r['methodSteps']))
    def test_pilot_and_time_uncertainty(self):
        self.assertEqual(len(PILOT),12)
        self.assertEqual(self.recipes['moong-dal-chilla']['timing']['prerequisiteMinutes'],[180,240])
        self.assertIsNone(self.recipes['korean-egg-rice-bowl']['timing']['prerequisiteMinutes'])
    def test_fixed_source_contradictions(self):
        r=self.recipes['phulka-soft-chapati']
        self.assertNotIn('2 cups',r['ingredients'][0]['items'][0]['note'])
        self.assertNotIn('30 g',' '.join(r['steps']))
        self.assertNotIn('7 tbsp',json.dumps(self.recipes['moong-dal-chilla']))
    def test_regional_sources_and_method_amounts(self):
        import re
        from nutrition import add, rounded, scaled
        for r in self.recipes.values():
            if not r.get('contentReview'): continue
            self.assertGreaterEqual(len(r['sources']),2)
            self.assertFalse(r['review']['kitchenTested'])
            items={i['id']:i for g in r['ingredients'] for i in g['items']}
            used=set(re.findall(r'\{\{([a-z0-9-]+)\}\}', ' '.join(r['stepTemplates'])))
            self.assertEqual(used,set(items),r['id'])
            self.assertNotIn('{{',' '.join(r['steps']))
            totals={}
            for i in items.values():
                if i['key']!='water': add(totals,i['key'],i.get('nutritionGrams',i['grams']))
            self.assertEqual(r['nutr'],rounded(scaled(totals,1/r['yield'])))

    def test_retrieval_prioritizes_preparation(self):
        r=self.recipes['moong-dal-chilla']
        self.assertTrue(any(d['id'].startswith('prep-') for d in retrieve(r,'What should I prepare first?')))
    def test_no_model_network_by_default(self):
        with patch('cooking_assistant.urlopen',side_effect=AssertionError('unexpected network')):
            result=answer(self.recipes['moong-dal-chilla'],'How long does soaking take?')
        self.assertEqual(result['mode'],'Local recipe search · no model')
        self.assertTrue(result['evidence'])
    def test_missing_evidence_and_scope(self):
        r=self.recipes['phulka-soft-chapati']
        self.assertEqual(answer(r,'quasar extrapolation')['mode'],'Insufficient evidence')
        self.assertEqual(answer(r,'Predict bitcoin')['mode'],'Cooking-only scope')
        self.assertIn('review required',answer(r,'Is overnight raw chicken safe?')['mode'])
    def test_local_model_failure_falls_back(self):
        def unavailable(*args): raise OSError('offline')
        r=self.recipes['moong-dal-chilla']
        self.assertIn('fallback',answer(r,'What to prepare first?','test',unavailable)['mode'])
    def test_model_cannot_generate_recipe_facts(self):
        r=self.recipes['moong-dal-chilla']
        def fake(*args): return {'evidence_ids':['prep-1'],'insufficient':False,'invented':'Cook at 900 degrees'}
        result=answer(r,'What to prepare first?','test',fake)
        self.assertNotIn('900',json.dumps(result));self.assertEqual(len(result['evidence']),1)

if __name__=='__main__': unittest.main()
