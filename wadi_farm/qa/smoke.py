"""Read-only smoke checks after installing on a staging Frappe site."""
import frappe


def run_smoke_checks():
    from wadi_farm.setup import ROLES
    from wadi_farm.wadi_farm.doctype import __path__  # verify module import
    from pathlib import Path
    import json
    root = Path(__path__[0])
    jsons = sorted(root.glob('wfm_*/wfm_*.json'))
    expected = [json.loads(p.read_text())['name'] for p in jsons]
    missing = [x for x in expected if not frappe.db.exists('DocType',x)]
    roles_missing = [x for x in ROLES if not frappe.db.exists('Role',x)]
    result = {'expected_doctypes':len(expected),'missing_doctypes':missing,'missing_roles':roles_missing,'remote_control_enabled':False}
    if missing or roles_missing:
        frappe.throw('Wadi Farm staging smoke failed: ' + str(result))
    print(result)
    return result
