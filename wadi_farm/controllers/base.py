"""Shared integrity checks. Not a substitute for ERPNext stock or GL posting."""
import math

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class WFMDocument(Document):
    def validate(self):
        self._verify_farm_company()
        self._verify_link_scope()
        self._verify_quantities()
        self._verify_domain_rules()

    def _verify_farm_company(self):
        if self.doctype == "WFM Farm":
            return
        if self.get("farm") and self.get("company"):
            company = frappe.db.get_value("WFM Farm", self.farm, "company")
            if company != self.company:
                frappe.throw("Farm and Company do not match")

    def _verify_link_scope(self):
        # Prevent a record in Farm A from referring to a facility, bird, pond, etc. in Farm B.
        for df in self.meta.get_link_fields():
            target = df.options
            value = self.get(df.fieldname)
            if not value or not target or not target.startswith("WFM ") or target == "WFM Farm":
                continue
            if target == self.doctype and value == self.name:
                frappe.throw("A document cannot refer to itself")
            linked = frappe.db.get_value(target, value, ["farm", "company"], as_dict=True)
            if linked and (linked.farm != self.get("farm") or linked.company != self.get("company")):
                frappe.throw(f"Linked {target} belongs to a different farm or company")

    def _verify_quantities(self):
        for df in self.meta.fields:
            if df.fieldtype not in ("Float", "Currency", "Int"):
                continue
            value = self.get(df.fieldname)
            if value is None or value == "":
                continue
            number = float(value)
            if not math.isfinite(number):
                frappe.throw(f"{df.label}: only finite values are allowed")
            non_negative = (
                df.fieldname.startswith(("count", "eggs_", "initial_count", "opening_count", "quantity", "fish_count", "bird_count", "offspring_count", "live_births", "stillbirths"))
                or df.fieldname.endswith(("_kg", "_liters", "_m3", "_m2", "_feddan", "_hours", "_percent", "_ppm"))
                or any(part in df.fieldname for part in ("capacity", "volume", "area", "biomass", "mortality"))
            )
            if non_negative and number < 0:
                frappe.throw(f"{df.label} cannot be negative")

    def _verify_domain_rules(self):
        t = self.doctype
        if t == "WFM User Farm Access":
            # Assignments must be one active entry per user and farm.
            match = frappe.db.get_value("WFM User Farm Access", {"user": self.user, "farm": self.farm, "status": "Active"}, "name")
            if self.status == "Active" and match and match != self.name:
                frappe.throw("User already has an active assignment for this farm")
        if t == "WFM Water Tank" and self.operating_volume_m3 and self.volume_m3:
            if self.operating_volume_m3 > self.volume_m3:
                frappe.throw("Operating volume must not exceed tank capacity")
        if t == "WFM Bird Pair":
            if self.male == self.female:
                frappe.throw("A breeding pair requires two distinct birds")
            for field, sex in (("male", "Male"), ("female", "Female")):
                bird_sex = frappe.db.get_value("WFM Bird", self.get(field), "sex")
                if bird_sex != sex:
                    frappe.throw(f"{field.title()} bird must have sex '{sex}'")
        if t == "WFM Bird Clutch":
            for part, total in (("fertile_count", "egg_count"), ("hatched_count", "egg_count"), ("live_chicks", "hatched_count")):
                a, b = self.get(part), self.get(total)
                if a is not None and b is not None and a > b:
                    frappe.throw(f"{part} cannot exceed {total}")
        if t == "WFM Egg Collection":
            total = (self.eggs_saleable or 0) + (self.eggs_broken or 0) + (self.eggs_for_hatching or 0)
            if total > (self.eggs_total or 0):
                frappe.throw("Egg allocations cannot exceed eggs collected")
        if t == "WFM Bird Mortality" and self.bird and self.count != 1:
            frappe.throw("An individually identified bird mortality must have count = 1")
        if t == "WFM Bird Transfer" and self.from_flock and self.from_flock == self.to_flock:
            frappe.throw("Source and destination flocks must differ")
        if t == "WFM Fish Transfer" and self.from_cycle == self.to_cycle:
            frappe.throw("Source and destination fish cycles must differ")
        if t == "WFM Drying Batch" and self.output_weight_kg is not None and self.input_weight_kg is not None:
            if self.output_weight_kg > self.input_weight_kg:
                frappe.throw("Dry output must not exceed input without an approved adjustment")
        if t == "WFM Irrigation Event":
            if self.start_at and self.end_at and get_datetime(self.end_at) < get_datetime(self.start_at):
                frappe.throw("Irrigation end time cannot precede start time")
            if self.meter_before is not None and self.meter_after is not None and self.meter_after < self.meter_before:
                frappe.throw("Meter reading cannot decrease without a rollover correction")
        if t == "WFM Device" and self.control_enabled:
            frappe.throw("Remote actuation is disabled in this pre-production release")
        if t == "WFM Device Command" and self.approval_state not in ("Proposed", "Denied", "Expired"):
            frappe.throw("Only non-executable proposed commands are allowed")
