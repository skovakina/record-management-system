"""Unit tests for Client records: required fields, save and reload."""

import os
import sys
import tempfile
import unittest

# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record import storage
from record.client import FIELDS, RECORD_TYPE, create_client_record, is_client_record
from record.store import RecordStore


class TestClientRecord(unittest.TestCase):
    def test_has_all_required_fields(self):
        record = create_client_record(1, "Ada Lovelace")
        # Every field from the brief is present, and no extras leaked in.
        self.assertEqual(set(record.keys()), set(FIELDS))

    def test_type_and_id_are_set(self):
        record = create_client_record("42", "Grace Hopper")
        self.assertEqual(record["type"], RECORD_TYPE)
        self.assertEqual(record["id"], 42)  # coerced to int
        self.assertIsInstance(record["id"], int)

    def test_field_values_are_stored(self):
        record = create_client_record(
            7,
            "Alan Turing",
            address_line_1="78 High Holborn",
            city="London",
            country="UK",
            phone_number="+44 20 1234 5678",
        )
        self.assertEqual(record["name"], "Alan Turing")
        self.assertEqual(record["address_line_1"], "78 High Holborn")
        self.assertEqual(record["city"], "London")
        self.assertEqual(record["country"], "UK")
        self.assertEqual(record["phone_number"], "+44 20 1234 5678")

    def test_is_client_record(self):
        self.assertTrue(is_client_record(create_client_record(1, "X")))
        self.assertFalse(is_client_record({"type": "Airline"}))
        self.assertFalse(is_client_record("not a dict"))


class TestClientPersistence(unittest.TestCase):
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
        store.add_client(1, "Ada Lovelace", city="London")
        self.assertIsInstance(store.records, list)
        self.assertEqual(len(store.records), 1)
        self.assertIsInstance(store.records[0], dict)

    def test_save_then_reload_round_trip(self):
        store = RecordStore(self.path)
        store.add_client(1, "Ada Lovelace", city="London", country="UK")
        store.add_client(2, "Grace Hopper", state="NY")
        store.save()

        # Simulate restarting the app: a fresh store loads from the same file.
        reloaded = RecordStore(self.path)
        reloaded.load()

        self.assertEqual(reloaded.records, store.records)
        self.assertEqual(reloaded.records[0]["name"], "Ada Lovelace")
        self.assertEqual(reloaded.records[1]["id"], 2)


if __name__ == "__main__":
    unittest.main()
