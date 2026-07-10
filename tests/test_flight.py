"""Unit tests for Flight records."""

import dataclasses
import os
import sys
import unittest

# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record.flight import Flight


class TestFlightRecord(unittest.TestCase):
    def test_has_all_required_fields(self):
        record = Flight(1, 2, "2026-07-07T09:00", "London", "Paris").to_dict()
        expected_fields = {f.name for f in dataclasses.fields(Flight)}
        self.assertEqual(set(record.keys()), expected_fields)

    def test_ids_are_coerced_to_int(self):
        record = Flight("10", "20", "2026-07-07", "London", "Paris").to_dict()
        self.assertEqual(record["client_id"], 10)
        self.assertEqual(record["airline_id"], 20)
        self.assertIsInstance(record["client_id"], int)
        self.assertIsInstance(record["airline_id"], int)

    def test_field_values_are_stored(self):
        record = Flight(1, 2, "2026-07-07T09:00", "London", "Paris").to_dict()
        self.assertEqual(record["date"], "2026-07-07T09:00")
        self.assertEqual(record["start_city"], "London")
        self.assertEqual(record["end_city"], "Paris")


if __name__ == "__main__":
    unittest.main()
