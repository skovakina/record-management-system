import json
import os
import sys
import tempfile
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from record import storage
from record.store import RecordStore


class TestStorageLoading(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.paths = {
            name: os.path.join(self.temp_dir.name, f"{name}.json")
            for name in storage.COLLECTION_TYPES
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_collection(self, name, records):
        with open(self.paths[name], "w", encoding="utf-8") as file:
            json.dump(records, file)

    def test_store_loads_three_collections(self):
        self.write_collection(
            "clients",
            [
                {
                    "id": "5e2e9a10-fc8d-48a3-8c5a-55225b08ad3f",
                    "name": "Maya Brooks",
                    "type": "client",
                }
            ],
        )
        self.write_collection(
            "airlines",
            [
                {
                    "id": "137758b0-f491-45dd-99fa-8f1deea6dc7a",
                    "company_name": "Airline 1",
                    "type": "airline",
                }
            ],
        )
        self.write_collection(
            "flights",
            [
                {
                    "client_id": "5e2e9a10-fc8d-48a3-8c5a-55225b08ad3f",
                    "airline_id": "137758b0-f491-45dd-99fa-8f1deea6dc7a",
                    "date": "2026-08-15T09:30",
                    "start_city": "Seattle",
                    "end_city": "Denver",
                    "type": "flight",
                }
            ],
        )

        collections = RecordStore(self.paths).load_records()

        self.assertEqual(set(collections), {"clients", "airlines", "flights"})
        self.assertEqual(collections["clients"][0]["name"], "Maya Brooks")
        self.assertEqual(collections["airlines"][0]["company_name"], "Airline 1")
        self.assertEqual(
            collections["flights"][0]["client_id"],
            "5e2e9a10-fc8d-48a3-8c5a-55225b08ad3f",
        )

    def test_default_dummy_data_loads(self):
        collections = RecordStore().load_records()

        self.assertEqual(len(collections["clients"]), 3)
        self.assertEqual(len(collections["airlines"]), 3)
        self.assertEqual(len(collections["flights"]), 3)
        self.assertEqual(collections["clients"][0]["name"], "Maya Brooks")

        client_ids = {client["id"] for client in collections["clients"]}
        airline_ids = {airline["id"] for airline in collections["airlines"]}
        for flight in collections["flights"]:
            self.assertIn(flight["client_id"], client_ids)
            self.assertIn(flight["airline_id"], airline_ids)


if __name__ == "__main__":
    unittest.main()
