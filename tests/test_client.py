"""Unit tests for Client records."""

import dataclasses
import os
import sys
import unittest

# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record.client import Client


class TestClientRecord(unittest.TestCase):
    def test_has_all_required_fields(self):
        record = Client(1, "Maya Brooks").to_dict()
        expected_fields = {f.name for f in dataclasses.fields(Client)}
        self.assertEqual(set(record.keys()), expected_fields)

    def test_type_and_id_are_set(self):
        record = Client("42", "Noah Patel").to_dict()
        self.assertEqual(record["type"], Client.type)
        self.assertEqual(record["id"], 42)
        self.assertIsInstance(record["id"], int)

    def test_field_values_are_stored(self):
        record = Client(
            7,
            "Elena Rivera",
            address_line_1="300 Lake Avenue",
            city="San Francisco",
            country="USA",
            phone_number="+1 415 555 0103",
        ).to_dict()
        self.assertEqual(record["name"], "Elena Rivera")
        self.assertEqual(record["address_line_1"], "300 Lake Avenue")
        self.assertEqual(record["city"], "San Francisco")
        self.assertEqual(record["country"], "USA")
        self.assertEqual(record["phone_number"], "+1 415 555 0103")


if __name__ == "__main__":
    unittest.main()
