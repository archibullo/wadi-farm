"""Authenticated, idempotent intake for field notes. NO ERP stock postings."""
import json
import frappe
from wadi_farm.utils.field_validation import validate_event_payload, payload_hash


def _authenticated():
    if frappe.session.user == "Guest":
        frappe.throw("Sign in to Wadi Farm", frappe.PermissionError)


@frappe.whitelist(methods=["GET"])
def get_mobile_context():
    _authenticated()
    allowed = _allowed_farms()
    if not allowed:
        return {"user": frappe.session.user, "csrf_token": getattr(frappe.session.data, "csrf_token", ""), "farms": [], "fields": [], "intake": "draft_only"}
    farms = frappe.get_list("WFM Farm", filters={"name": ["in", allowed]}, fields=["name", "farm_name", "company"], limit_page_length=200)
    fields = frappe.get_list("WFM Field", filters={"farm": ["in", allowed]}, fields=["name", "field_name", "farm"], limit_page_length=1000)
    return {
        "user": frappe.session.user,
        "csrf_token": getattr(frappe.session.data, "csrf_token", ""),
        "farms": farms, "fields": fields,
        "intake": "draft_only",
    }


def _allowed_farms():
    if "System Manager" in frappe.get_roles(frappe.session.user):
        return frappe.get_list("WFM Farm", pluck="name", limit_page_length=2000)
    return frappe.get_all("WFM User Farm Access", filters={"user": frappe.session.user, "status": "Active"}, pluck="farm", limit_page_length=2000)


def _farm_allowed(farm):
    return farm in _allowed_farms() and bool(frappe.get_list("WFM Farm", filters={"name": farm}, fields=["name"], limit_page_length=1))


def _field_allowed(field, farm):
    if not field:
        return True
    return bool(frappe.get_list("WFM Field", filters={"name": field, "farm": farm}, fields=["name"], limit_page_length=1))


@frappe.whitelist(methods=["POST"])
def sync_batch(events):
    _authenticated()
    if isinstance(events, str):
        events = json.loads(events)
    if not isinstance(events, list) or not 1 <= len(events) <= 50:
        frappe.throw("Expected 1 to 50 events")
    frappe.has_permission("WFM Field Log", "create", throw=True)
    results = []
    for index, raw in enumerate(events):
        sp = f"wf_mobile_{index}"
        frappe.db.savepoint(sp)
        client_id = str(raw.get("client_event_uuid", "")) if isinstance(raw, dict) else ""
        try:
            clean = validate_event_payload(raw)
            signature = payload_hash(clean)
            if not _farm_allowed(clean["farm"]) or not _field_allowed(clean["field"], clean["farm"]):
                raise ValueError("Farm or field is not accessible")
            existing = frappe.db.get_value("WFM Field Log", {"client_event_uuid": clean["client_event_uuid"]}, ["name", "payload_sha256"], as_dict=True)
            if existing:
                if existing.payload_sha256 != signature:
                    results.append({"id": client_id, "status": "conflict"})
                else:
                    results.append({"id": client_id, "status": "duplicate", "name": existing.name})
                continue
            company = frappe.db.get_value("WFM Farm", clean["farm"], "company")
            doc = frappe.get_doc({
                "doctype": "WFM Field Log", "company": company,
                "farm": clean["farm"], "field": clean["field"],
                "client_event_uuid": clean["client_event_uuid"],
                "payload_sha256": signature, "event_at": clean["event_at"],
                "activity_type": clean["activity_type"], "quantity": clean["quantity"],
                "unit": clean["unit"], "notes": clean["notes"],
                "device_id": clean["device_id"], "synced_by": frappe.session.user,
                "status": "Draft",
            })
            doc.insert()  # Frappe verifies user permission, standard validation and transactions.
            results.append({"id": client_id, "status": "created", "name": doc.name})
        except (ValueError, frappe.ValidationError, frappe.PermissionError) as exc:
            frappe.db.rollback(save_point=sp)
            results.append({"id": client_id, "status": "rejected", "reason": str(exc)[:200]})
        except Exception:
            frappe.db.rollback(save_point=sp)
            frappe.log_error(title="Wadi Farm mobile sync failed")
            results.append({"id": client_id, "status": "retry"})
    return {"results": results, "side_effects": "none; no stock or financial posting"}
