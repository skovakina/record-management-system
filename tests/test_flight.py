"""Unit tests for Flight records: required fields, save and reload."""

import os
import sys
import tempfile
import unittest

# Make ``src`` importable when running ``python -m unittest`` from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record import storage  # noqa: E402
from record.flight import FIELDS, create_flight_record, is_flight_record  # noqa: E402
from record.store import RecordStore  # noqa: E402


class TestFlightRecord(unittest.TestCase):
    def test_has_all_required_fields(self):
        record = create_flight_record(1, 2, "2026-07-07T09:00", "London", "Paris")
        # Every field from the brief is present, and no extras leaked in.
        self.assertEqual(set(record.keys()), set(FIELDS))

    def test_ids_are_coerced_to_int(self):
        record = create_flight_record("10", "20", "2026-07-07", "London", "Paris")
        self.assertEqual(record["Client_ID"], 10)
        self.assertEqual(record["Airline_ID"], 20)
        self.assertIsInstance(record["Client_ID"], int)
        self.assertIsInstance(record["Airline_ID"], int)

    def test_field_values_are_stored(self):
        record = create_flight_record(1, 2, "2026-07-07T09:00", "London", "Paris")
        self.assertEqual(record["Date"], "2026-07-07T09:00")
        self.assertEqual(record["Start City"], "London")
        self.assertEqual(record["End City"], "Paris")

    def test_is_flight_record(self):
        self.assertTrue(is_flight_record(create_flight_record(1, 2, "d", "A", "B")))
        self.assertFalse(is_flight_record({"Type": "Client", "ID": 1}))
        self.assertFalse(is_flight_record("not a dict"))


class TestFlightPersistence(unittest.TestCase):
    def setUp(self):
        # A throwaway JSONL file per test so runs never touch real data.
        fd, self.path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        os.remove(self.path)  # RecordStore should treat a missing file as empty.

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

        # Simulate restarting the app: a fresh store loads from the same file.
        reloaded = RecordStore(self.path)
        reloaded.load()

        self.assertEqual(reloaded.records, store.records)
        self.assertEqual(reloaded.records[0]["Start City"], "London")
        self.assertEqual(reloaded.records[1]["Airline_ID"], 4)


if __name__ == "__main__":
    unittest.main()
