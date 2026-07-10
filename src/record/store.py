"""In-memory record collections loaded from JSON files."""

from record import storage
from record.airline import Airline
from record.client import Client
from record.flight import Flight


class RecordStore:
    def __init__(self, collection_paths=None):
        if collection_paths is None:
            collection_paths = storage.DEFAULT_COLLECTION_PATHS

        self.collection_paths = dict(collection_paths)
        self.records = {name: [] for name in storage.COLLECTION_TYPES}

    def load(self):
        self.records = storage.load_collections(self.collection_paths)
        return self.records

    def save(self):
        """Save the current records."""
        storage.save_collections(self.records, self.collection_paths)

    def add_client(self, id, name, **fields):
        record = Client(id, name, **fields).to_dict()
        self.records["clients"].append(record)
        return record

    def add_airline(self, id, company_name):
        record = Airline(id, company_name).to_dict()
        self.records["airlines"].append(record)
        return record

    def add_flight(self, client_id, airline_id, date, start_city, end_city):
        record = Flight(client_id, airline_id, date, start_city, end_city).to_dict()
        self.records["flights"].append(record)
        return record
