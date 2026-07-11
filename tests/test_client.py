"""Unit tests for Client records: required fields, save and reload."""

import dataclasses
import os
import sys
import tempfile
import unittest
import uuid

# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record import storage
from record.client import Client
from record.store import RecordStore


class TestClientRecord(unittest.TestCase):
    def test_has_all_required_fields(self):
        record = Client("Ada Lovelace").to_dict()
        expected_fields = {f.name for f in dataclasses.fields(Client)}
        self.assertEqual(set(record.keys()), expected_fields)

    def test_type_and_id_are_set(self):
        record = Client("Grace Hopper").to_dict()
        self.assertEqual(record["type"], Client.type)
        self.assertIsInstance(record["id"], str)
        uuid.UUID(record["id"])  # raises ValueError if not a valid UUID

    def test_ids_are_unique(self):
        first = Client("Ada Lovelace").to_dict()
        second = Client("Ada Lovelace").to_dict()
        self.assertNotEqual(first["id"], second["id"])

    def test_field_values_are_stored(self):
        record = Client(
            "Alan Turing",
            address_line_1="78 High Holborn",
            city="London",
            country="UK",
            phone_number="+44 20 1234 5678",
        ).to_dict()
        self.assertEqual(record["name"], "Alan Turing")
        self.assertEqual(record["address_line_1"], "78 High Holborn")
        self.assertEqual(record["city"], "London")
        self.assertEqual(record["country"], "UK")
        self.assertEqual(record["phone_number"], "+44 20 1234 5678")


class TestClientPersistence(unittest.TestCase):
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
        store.add_client("Ada Lovelace", city="London")
        self.assertIsInstance(store.records, list)
        self.assertEqual(len(store.records), 1)
        self.assertIsInstance(store.records[0], dict)

    def test_save_then_reload_round_trip(self):
        store = RecordStore(self.path)
        store.add_client("Ada Lovelace", city="London", country="UK")
        store.add_client("Grace Hopper", state="NY")
        store.save()

        reloaded = RecordStore(self.path)
        reloaded.load()

        self.assertEqual(reloaded.records, store.records)
        self.assertEqual(reloaded.records[0]["name"], "Ada Lovelace")
        uuid.UUID(reloaded.records[1]["id"])


if __name__ == "__main__":
    unittest.main()
