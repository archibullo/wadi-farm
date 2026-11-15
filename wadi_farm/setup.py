import frappe

ROLES = (
    "Farm Manager", "Farm Supervisor", "Farm Operator",
    "Farm Veterinarian", "Farm Technician", "Farm Auditor",
    "Farm Integrator",
)

def before_install():
    for role in ROLES:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)

def after_install():
    frappe.logger("wadi_farm").info("Wadi Farm installed. Configure company and farm permissions before adding users.")
