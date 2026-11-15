"""Authenticated farm module directory; lists only permitted DocTypes."""
from pathlib import Path
import json
import frappe

no_cache = 1

LABELS = {
    "Land": "الأراضي والحقول", "Crop": "المحاصيل والعمليات الزراعية",
    "Water": "المياه والري", "Livestock": "الأبقار والأغنام",
    "Poultry": "الطيور والحمام والدواجن", "Aquaculture": "الاستزراع السمكي",
    "Greenhouse": "الصوب والتحكم المناخي", "Machinery": "المعدات والصيانة والطاقة",
    "Processing": "الحصاد والتجفيف والتعبئة", "Operations": "التشغيل والعمالة والصلاحيات",
    "Integrations": "الأجهزة والأرصاد والأقمار الصناعية", "Compliance": "الجودة والمخاطر والسلامة",
}

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/farm_dashboard"
        raise frappe.Redirect
    context.title = "Wadi Farm / إدارة المزرعة"
    catalog = json.loads((Path(__file__).resolve().parents[1] / "feature_registry.json").read_text(encoding="utf-8"))
    context.groups = []
    for group, names in catalog.items():
        allowed = [
            {"name": name, "slug": frappe.scrub(name).replace("_", "-")}
            for name in names if frappe.has_permission(name, "read")
        ]
        if allowed:
            context.groups.append({"title": LABELS.get(group, group), "models": allowed})
