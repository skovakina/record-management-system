"""Unit tests for Airline records: required fields, save and reload."""

import dataclasses
import os
import sys
import tempfile
import unittest
import uuid

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record import storage
from record.airline import Airline
from record.store import RecordStore


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


class TestAirlinePersistence(unittest.TestCase):
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
        store.add_airline("British Airways")
        self.assertIsInstance(store.records, list)
        self.assertEqual(len(store.records), 1)
        self.assertIsInstance(store.records[0], dict)

    def test_save_then_reload_round_trip(self):
        store = RecordStore(self.path)
        store.add_airline("British Airways")
        store.add_airline("Emirates")
        store.save()

        reloaded = RecordStore(self.path)
        reloaded.load()

        self.assertEqual(reloaded.records, store.records)
        self.assertEqual(reloaded.records[0]["company_name"], "British Airways")
        uuid.UUID(reloaded.records[1]["id"])


if __name__ == "__main__":
    unittest.main()
