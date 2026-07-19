"""Unit tests for record.validation — required fields and references."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, "src"))

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
            "phone_number": "020 7946 0958",
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
        self.assertEqual(validation.validate("airline", {"company_name": "BA"}), {})

    def test_id_and_type_are_never_required(self):
        # A complete airline with no id/type still validates.
        self.assertEqual(
            validation.missing_fields("airline", {"company_name": "BA"}), []
        )


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


class TestPhoneFormat(unittest.TestCase):
    def _client(self, phone):
        return {
            "name": "Ada",
            "address_line_1": "1 Way",
            "city": "London",
            "state": "London",
            "zip_code": "EC1",
            "country": "UK",
            "phone_number": phone,
        }

    def test_plain_digits_valid(self):
        self.assertEqual(validation.validate("client", self._client("0123456789")), {})

    def test_international_with_separators_valid(self):
        self.assertEqual(
            validation.validate("client", self._client("+44 (20) 7946-0958")), {}
        )

    def test_too_few_digits_flagged(self):
        errors = validation.validate("client", self._client("123"))
        self.assertEqual(errors.get("phone_number"), "invalid format")

    def test_letters_flagged(self):
        errors = validation.validate("client", self._client("12ab567"))
        self.assertEqual(errors.get("phone_number"), "invalid format")


class TestAirlineUniqueness(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"id": "a1", "type": "airline", "company_name": "British Airways"},
            {"id": "c1", "type": "client", "name": "British Airways"},
        ]

    def test_duplicate_name_flagged(self):
        errors = validation.validate(
            "airline", {"company_name": "British Airways"}, self.records
        )
        self.assertEqual(errors.get("company_name"), "duplicate")

    def test_duplicate_is_case_and_space_insensitive(self):
        # An airline named "British Airways" already exists. Adding it
        # again with different casing and extra spaces should be caught
        same_name_messier = {"company_name": "  british airways "}

        errors = validation.validate("airline", same_name_messier, self.records)

        self.assertEqual(errors.get("company_name"), "duplicate")

    def test_distinct_name_valid(self):
        self.assertEqual(
            validation.validate("airline", {"company_name": "easyJet"}, self.records),
            {},
        )

    def test_editing_same_record_is_not_a_duplicate(self):
        errors = validation.validate(
            "airline",
            {"company_name": "British Airways"},
            self.records,
            exclude_id="a1",
        )
        self.assertEqual(errors, {})

    def test_uniqueness_skipped_without_records(self):
        self.assertEqual(
            validation.validate("airline", {"company_name": "British Airways"}), {}
        )


class TestFlightCityLogic(unittest.TestCase):
    def _flight(self, start, end):
        return {
            "type": "flight",
            "client_id": "c1",
            "airline_id": "a1",
            "date": "2026-07-07T09:00",
            "start_city": start,
            "end_city": end,
        }

    def test_same_start_and_end_flagged(self):
        errors = validation.validate("flight", self._flight("London", "London"))
        self.assertEqual(errors.get("start_city"), "same as end city")
        self.assertEqual(errors.get("end_city"), "same as start city")

    def test_same_city_is_case_and_space_insensitive(self):
        errors = validation.validate("flight", self._flight("London", "  london "))
        self.assertIn("start_city", errors)
        self.assertIn("end_city", errors)

    def test_different_cities_valid(self):
        errors = validation.validate("flight", self._flight("London", "Paris"))
        self.assertNotIn("start_city", errors)
        self.assertNotIn("end_city", errors)


if __name__ == "__main__":
    unittest.main()
