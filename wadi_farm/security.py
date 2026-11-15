"""Additional per-farm restrictions, supplementing built-in DocPerm/User Permissions."""
import frappe


def _privileged(user):
    return user == "Administrator" or "System Manager" in frappe.get_roles(user)


def _allowed(user):
    if _privileged(user):
        return None
    return frappe.get_all(
        "WFM User Farm Access",
        filters={"user": user, "status": "Active"},
        pluck="farm", limit_page_length=2000,
    )


def _sql_filter(field_name, user):
    allowed = _allowed(user)
    if allowed is None:
        return ""
    if not allowed:
        return "1=0"
    # Only internal SQL values from Farm Assignment records; every value is escaped.
    quoted = ", ".join(frappe.db.escape(name) for name in allowed)
    return f"{field_name} IN ({quoted})"


def farm_query_conditions(user=None):
    return _sql_filter("`tabWFM Farm`.`name`", user or frappe.session.user)


def scoped_query_conditions(user=None):
    return _sql_filter("`farm`", user or frappe.session.user)


def has_document_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if _privileged(user):
        return None  # retain ordinary Frappe role permissions
    # Role permissions still run. This only denies cross-farm access.
    allowed = _allowed(user) or []
    if isinstance(doc, str) or doc is None:
        return None  # create permission checks occur before a farm is selected
    farm = doc.name if doc.doctype == "WFM Farm" else doc.get("farm")
    if not farm:
        return None if permission_type == "create" else False
    if farm not in allowed:
        return False
    return None
