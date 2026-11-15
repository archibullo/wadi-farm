app_name = "wadi_farm"
app_title = "Wadi Farm"
app_publisher = "Wadi Farm"
app_description = "Integrated agriculture, livestock, poultry and farm operations for ERPNext"
app_email = ""
app_license = "MIT"
app_version = "0.4.0a0"
required_apps = ["erpnext"]

app_logo_url = "/assets/wadi_farm/logo.svg"
add_to_apps_screen = [{
    "name": "wadi_farm",
    "logo": "/assets/wadi_farm/logo.svg",
    "title": "Wadi Farm",
    "route": "/farm_dashboard",
}]

before_install = "wadi_farm.setup.before_install"
after_install = "wadi_farm.setup.after_install"

# Device-control integrations must never be auto-enabled by hooks.

# Farm access never relies solely on client-side filters.
from wadi_farm.security_types import WFM_DOCTYPES
has_permission = {dt: "wadi_farm.security.has_document_permission" for dt in WFM_DOCTYPES}
permission_query_conditions = {
    dt: "wadi_farm.security.farm_query_conditions" if dt == "WFM Farm"
    else "wadi_farm.security.scoped_query_conditions"
    for dt in WFM_DOCTYPES
}
