"""Unit tests for record.validation — required fields and references."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record import validation


class TestRequiredFields(unittest.TestCase):
    def test_complete_client_is_valid(self):
        data = {
            "name": "Ada Lovelace",
            "address_line_1": "1 Analytical Way",
            "city": "London",
            "state": "London",
            "zip_code": "EC1",
            "country": "UK",
            "phone_number": "123",
        }
        self.assertEqual(validation.validate("client", data), {})

    def test_missing_required_client_fields_flagged(self):
        errors = validation.validate("client", {"name": "Ada"})
        self.assertIn("city", errors)
        self.assertIn("phone_number", errors)
        self.assertNotIn("name", errors)  # provided
        self.assertNotIn("address_line_2", errors)  # optional

    def test_blank_and_whitespace_count_as_missing(self):
        errors = validation.validate("airline", {"company_name": "   "})
        self.assertEqual(errors, {"company_name": "required"})

    def test_airline_minimal_valid(self):
        self.assertEqual(
            validation.validate("airline", {"company_name": "BA"}), {}
        )

    def test_id_and_type_are_never_required(self):
        # A complete airline with no id/type still validates.
        self.assertEqual(validation.missing_fields("airline", {"company_name": "BA"}), [])


class TestReferenceIntegrity(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": "c1", "type": "client", "name": "Ada"},
            {"id": "a1", "type": "airline", "company_name": "BA"},
        ]
        self.flight = {
            "type": "flight",
            "client_id": "c1",
            "airline_id": "a1",
            "date": "2026-07-07T09:00",
            "start_city": "London",
            "end_city": "Paris",
        }

    def test_valid_references_pass(self):
        self.assertEqual(validation.validate("flight", self.flight, self.records), {})

    def test_unknown_client_reference_flagged(self):
        bad = dict(self.flight, client_id="nope")
        errors = validation.validate("flight", bad, self.records)
        self.assertEqual(errors.get("client_id"), "unknown reference")

    def test_unknown_airline_reference_flagged(self):
        bad = dict(self.flight, airline_id="nope")
        errors = validation.validate("flight", bad, self.records)
        self.assertEqual(errors.get("airline_id"), "unknown reference")

    def test_missing_reference_reports_required_not_unknown(self):
        bad = dict(self.flight, client_id="")
        errors = validation.validate("flight", bad, self.records)
        self.assertEqual(errors.get("client_id"), "required")

    def test_references_skipped_without_records(self):
        bad = dict(self.flight, client_id="nope")
        # No records supplied -> reference check is skipped, only required runs.
        self.assertEqual(validation.validate("flight", bad), {})


if __name__ == "__main__":
    unittest.main()
