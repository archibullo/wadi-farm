"""Read-only manual ingestion bridge; no device actuation endpoints."""
import json
from datetime import datetime, timezone
import frappe


@frappe.whitelist(methods=["POST"])
def record_reading(channel, observed_at, numeric_value, source_event_id=None):
    if frappe.session.user == "Guest":
        frappe.throw("Authentication required", frappe.PermissionError)
    frappe.has_permission("WFM Telemetry Observation", "create", throw=True)
    ch = frappe.get_doc("WFM Device Channel", channel)
    ch.check_permission("read")
    device = frappe.get_doc("WFM Device", ch.device)
    device.check_permission("read")
    if not frappe.get_list("WFM Farm", filters={"name": ch.farm}, fields=["name"], limit_page_length=1):
        frappe.throw("Device farm is not accessible", frappe.PermissionError)
    from wadi_farm.utils.field_validation import payload_hash
    from frappe.utils import get_datetime
    try:
        value = float(numeric_value)
        import math
        if not math.isfinite(value):
            raise ValueError()
    except (TypeError, ValueError):
        frappe.throw("Reading must be a finite number")
    dt = get_datetime(observed_at)
    if not dt:
        frappe.throw("A valid timestamp is required")
    key = payload_hash({"channel": channel, "timestamp": str(dt), "source_id": str(source_event_id or ""), "numeric_value": value})
    existing = frappe.db.get_value("WFM Telemetry Observation", {"deduplication_key": key}, "name")
    if existing:
        return {"name": existing, "status": "duplicate"}
    doc = frappe.get_doc({
        "doctype": "WFM Telemetry Observation", "company": ch.company, "farm": ch.farm,
        "channel": channel, "observed_at": dt, "numeric_value": value,
        "unit": ch.normalized_unit or ch.raw_unit,
        "source_event_id": str(source_event_id or "")[:140], "deduplication_key": key,
        "quality": "Valid",
    })
    doc.insert()
    return {"name": doc.name, "status": "created"}
