from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'wadi_farm' / 'wadi_farm' / 'doctype'

class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.models = {json.loads(p.read_text())['name']: json.loads(p.read_text()) for p in ROOT.glob('wfm_*/wfm_*.json')}
    def test_count(self):
        self.assertEqual(len(self.models),100)
    def test_poultry_present(self):
        for name in ['WFM Bird','WFM Bird Pair','WFM Egg Collection','WFM Bird Health','WFM Bird Flock','WFM User Farm Access']:
            self.assertIn(name,self.models)
    def test_all_links_resolvable(self):
        for name, model in self.models.items():
            for f in model['fields']:
                if f['fieldtype']=='Link' and f.get('options','').startswith('WFM '):
                    self.assertIn(f['options'],self.models, name)
    def test_command_restricted(self):
        roles=[x['role'] for x in self.models['WFM Device Command']['permissions']]
        self.assertEqual(roles,['System Manager','Farm Auditor'])

if __name__=='__main__':unittest.main()
