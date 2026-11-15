"""Validate self-contained app metadata; does not prove a Frappe site install."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1] / 'wadi_farm' / 'wadi_farm' / 'doctype'
files = list(ROOT.glob('wfm_*/wfm_*.json'))
assert len(files) >= 100, f'Expected at least 100 doctypes, got {len(files)}'
models = {json.loads(p.read_text(encoding='utf8'))['name']: json.loads(p.read_text(encoding='utf8')) for p in files}
assert len(models) == len(files)
for name, j in models.items():
    assert j['module'] == 'Wadi Farm'
    fields = j['fields']
    names = [x['fieldname'] for x in fields]
    assert len(names) == len(set(names)), f'Duplicate field in {name}'
    assert j['field_order'] == names, f'field_order mismatch {name}'
    assert j['title_field'] in names, f'title_field missing {name}'
    assert any(p['role']=='System Manager' for p in j['permissions'])
    assert j['custom'] == 0 and j['doctype'] == 'DocType'
    if name != 'WFM Farm':
        assert {'company','farm'} <= set(names), f'no company/farm {name}'
    for f in fields:
        if f['fieldtype'] == 'Link' and f.get('options','').startswith('WFM '):
            assert f['options'] in models, f'Broken link: {name}.{f["fieldname"]} -> {f["options"]}'
    snake = name.lower().replace(' ','_')
    controller = ROOT / snake / (snake + '.py')
    assert controller.is_file(), controller
    assert 'class ' + name.replace(' ','') in controller.read_text(), name
assert all(models['WFM Device Command']['permissions'][i]['role'] != 'Farm Operator' for i in range(len(models['WFM Device Command']['permissions'])))
print(f'PASS: {len(models)} DocTypes, links, permissions and controllers checked.')
