"""Unit tests for Flight records: required fields, save and reload."""

import dataclasses
import os
import sys
import tempfile
import unittest

# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record import storage
from record.flight import Flight
from record.store import RecordStore


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


class TestFlightPersistence(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        os.remove(self.path)

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_load_missing_file_returns_empty(self):
        self.assertEqual(storage.load_records(self.path), [])

    def test_records_stored_as_dicts_in_shared_list(self):
        store = RecordStore(self.path)
        store.add_flight(1, 2, "2026-07-07", "London", "Paris")
        self.assertIsInstance(store.records, list)
        self.assertEqual(len(store.records), 1)
        self.assertIsInstance(store.records[0], dict)

    def test_save_then_reload_round_trip(self):
        store = RecordStore(self.path)
        store.add_flight(1, 2, "2026-07-07T09:00", "London", "Paris")
        store.add_flight(3, 4, "2026-08-01T14:30", "Berlin", "Rome")
        store.save()

        reloaded = RecordStore(self.path)
        reloaded.load()

        self.assertEqual(reloaded.records, store.records)
        self.assertEqual(reloaded.records[0]["start_city"], "London")
        self.assertEqual(reloaded.records[1]["airline_id"], 4)


if __name__ == "__main__":
    unittest.main()
