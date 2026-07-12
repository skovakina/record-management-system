"""Keep records in memory while running."""

from record import storage
from record.airline import Airline
from record.client import Client
from record.flight import Flight

RECORD_CLASSES = {
    "clients": Client,
    "airlines": Airline,
    "flights": Flight,
}


class RecordStore:
    def __init__(self, collection_paths=storage.COLLECTION_PATHS):
        self.collection_paths = dict(collection_paths)
        self.records = {name: [] for name in storage.COLLECTION_TYPES}

    def load_records(self):
        loaded = storage.load_collections(self.collection_paths)
        for section in storage.COLLECTION_TYPES:
            self.records[section][:] = loaded[section]
        return self.records

    def save_records(self, section):
        path = self.collection_paths[section]
        storage.save_records(self.records[section], path)
        self.records[section][:] = storage.load_records(path)

    def add_record(self, section, fields):
        record_class = RECORD_CLASSES.get(section)
        record = record_class(**fields).to_dict()
        self.records[section].append(record)
        self.save_records(section)
