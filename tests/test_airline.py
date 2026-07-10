"""Unit tests for Airline records."""

import dataclasses
import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record.airline import Airline


class TestAirlineRecord(unittest.TestCase):
    def test_has_all_required_fields(self):
        record = Airline(1, "British Airways").to_dict()
        expected_fields = {f.name for f in dataclasses.fields(Airline)}
        self.assertEqual(set(record.keys()), expected_fields)

    def test_type_and_id_are_set(self):
        record = Airline("42", "Emirates").to_dict()
        self.assertEqual(record["type"], Airline.type)
        self.assertEqual(record["id"], 42)
        self.assertIsInstance(record["id"], int)

    def test_company_name_is_stored(self):
        record = Airline(7, "Qatar Airways").to_dict()
        self.assertEqual(record["company_name"], "Qatar Airways")


if __name__ == "__main__":
    unittest.main()
