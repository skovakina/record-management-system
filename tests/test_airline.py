"""Unit tests for Airline records."""

import dataclasses
import os
import sys
import unittest
import uuid

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record.airline import Airline


class TestAirlineRecord(unittest.TestCase):
    def test_has_all_required_fields(self):
        record = Airline("British Airways").to_dict()
        expected_fields = {f.name for f in dataclasses.fields(Airline)}
        self.assertEqual(set(record.keys()), expected_fields)

    def test_type_and_id_are_set(self):
        record = Airline("Emirates").to_dict()
        self.assertEqual(record["type"], Airline.type)
        self.assertIsInstance(record["id"], str)
        uuid.UUID(record["id"])  # raises ValueError if not a valid UUID

    def test_ids_are_unique(self):
        first = Airline("Qatar Airways").to_dict()
        second = Airline("Qatar Airways").to_dict()
        self.assertNotEqual(first["id"], second["id"])

    def test_company_name_is_stored(self):
        record = Airline("Qatar Airways").to_dict()
        self.assertEqual(record["company_name"], "Qatar Airways")

if __name__ == "__main__":
    unittest.main()
