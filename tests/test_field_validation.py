import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wadi_farm.utils.field_validation import validate_event_payload, payload_hash

BASE = {
    "client_event_uuid":"1d6c2c70-a30c-4dfa-8e23-2eed790977be",
    "farm":"farm-1", "field":"field-1", "activity_type":"Feeding",
    "event_at":"2026-11-15T10:00:00+02:00", "quantity":5, "unit":"kg",
    "notes":"test", "device_id":"tablet-1"
}

class FieldValidationTests(unittest.TestCase):
    def test_accepts_event(self):
        result=validate_event_payload(BASE)
        self.assertEqual(result['event_at'],'2026-11-15 08:00:00')
    def test_same_moment_different_zone_same_hash(self):
        other=dict(BASE,event_at='2026-11-15T08:00:00Z')
        self.assertEqual(payload_hash(validate_event_payload(BASE)), payload_hash(validate_event_payload(other)))
    def test_refuses_naive_time(self):
        with self.assertRaises(ValueError):validate_event_payload(dict(BASE,event_at='2026-11-15T10:00:00'))
    def test_refuses_invalid_uuid(self):
        with self.assertRaises(ValueError):validate_event_payload(dict(BASE,client_event_uuid='abc'))
    def test_refuses_negative_quantity(self):
        with self.assertRaises(ValueError):validate_event_payload(dict(BASE,quantity=-1))
    def test_refuses_non_finite_quantity(self):
        with self.assertRaises(ValueError):validate_event_payload(dict(BASE,quantity='NaN'))
    def test_refuses_unknown_activity(self):
        with self.assertRaises(ValueError):validate_event_payload(dict(BASE,activity_type='Open Valves'))
    def test_hash_ignores_unexpected_input(self):
        a=validate_event_payload(BASE)
        b=validate_event_payload(dict(BASE,untrusted='arbitrary'))
        self.assertEqual(payload_hash(a),payload_hash(b))
    def test_changed_payload_changes_hash(self):
        self.assertNotEqual(payload_hash(validate_event_payload(BASE)),payload_hash(validate_event_payload(dict(BASE,quantity=6))))
    def test_rejects_long_notes(self):
        with self.assertRaises(ValueError):validate_event_payload(dict(BASE,notes='x'*1001))

if __name__=='__main__':unittest.main()
