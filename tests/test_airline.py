"""Unit tests for Airline records."""

import unittest

from src.record.airline import (
    FIELDS,
    RECORD_TYPE,
    create_airline_record,
    is_airline_record,
)


class TestAirlineRecord(unittest.TestCase):
    """Tests for Airline record data model."""

    def test_has_all_required_fields(self):
        record = create_airline_record(1, "British Airways")

        self.assertEqual(set(record.keys()), set(FIELDS))

    def test_type_and_id_are_set(self):
        record = create_airline_record("42", "Emirates")

        self.assertEqual(record["Type"], RECORD_TYPE)
        self.assertEqual(record["ID"], 42)
        self.assertIsInstance(record["ID"], int)

    def test_company_name_is_set(self):
        record = create_airline_record(1, "Qatar Airways")

        self.assertEqual(record["Company Name"], "Qatar Airways")

    def test_is_airline_record_returns_true_for_airline(self):
        record = create_airline_record(1, "British Airways")

        self.assertTrue(is_airline_record(record))

    def test_is_airline_record_returns_false_for_other_record_type(self):
        record = {"ID": 1, "Type": "Client", "Name": "Alice"}

        self.assertFalse(is_airline_record(record))

    def test_is_airline_record_returns_false_for_non_dict(self):
        self.assertFalse(is_airline_record("Airline"))


if __name__ == "__main__":
    unittest.main()