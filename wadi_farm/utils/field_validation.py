"""Pure Python offline payload validation; callable without Frappe."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from uuid import UUID

ALLOWED_ACTIVITIES = {
    "Irrigation", "Feeding", "Observation", "Equipment",
    "Maintenance", "Harvest", "Safety", "Other",
}


def validate_event_payload(raw):
    if not isinstance(raw, dict):
        raise ValueError("Event must be an object")
    event_id = str(raw.get("client_event_uuid", ""))
    try:
        parsed_id = UUID(event_id)
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Invalid client_event_uuid") from None
    if parsed_id.version != 4 or str(parsed_id) != event_id.lower():
        raise ValueError("Event ID must be a canonical UUID v4")
    farm = str(raw.get("farm") or "").strip()
    field = str(raw.get("field") or "").strip()
    if not farm or len(farm) > 140 or len(field) > 140:
        raise ValueError("Invalid farm or field")
    activity = str(raw.get("activity_type") or "").strip()
    if activity not in ALLOWED_ACTIVITIES:
        raise ValueError("Invalid activity type")
    event_at = raw.get("event_at")
    if not isinstance(event_at, str):
        raise ValueError("event_at must be an ISO timestamp with timezone")
    try:
        parsed = datetime.fromisoformat(event_at.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("Invalid event_at") from None
    if parsed.tzinfo is None:
        raise ValueError("event_at must include timezone")
    if parsed.astimezone(timezone.utc).timestamp() < 946684800:
        raise ValueError("event_at is outside supported range")
    quantity = raw.get("quantity")
    if quantity in ("", None):
        quantity = None
    else:
        try:
            quantity = float(quantity)
        except (TypeError, ValueError):
            raise ValueError("Invalid quantity") from None
        if not math.isfinite(quantity) or quantity < 0:
            raise ValueError("Quantity must be finite and non-negative")
    notes = str(raw.get("notes") or "").strip()
    unit = str(raw.get("unit") or "").strip()
    device_id = str(raw.get("device_id") or "").strip()
    if len(notes) > 1000 or len(unit) > 40 or len(device_id) > 140:
        raise ValueError("Text exceeds field limit")
    normalized = {
        "client_event_uuid": event_id.lower(),
        "farm": farm,
        "field": field or None,
        "activity_type": activity,
        "event_at": parsed.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "quantity": quantity,
        "unit": unit,
        "notes": notes,
        "device_id": device_id,
    }
    return normalized


def payload_hash(normalized):
    return sha256(json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
