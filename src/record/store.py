"""Keep records in memory while running."""

from record import storage
from record.airline import Airline
from record.client import Client
from record.flight import Flight


class RecordStore:
    def __init__(self, collection_paths=storage.COLLECTION_PATHS):
        self.collection_paths = dict(collection_paths)
        self.records = {name: [] for name in storage.COLLECTION_TYPES}

    def load_records(self):
        self.records = storage.load_collections(self.collection_paths)
        return self.records

    def save_records(self):
        storage.save_collections(self.records, self.collection_paths)

    def add_client_record(self, name, **fields):
        record = Client(name, **fields).to_dict()
        self.records["clients"].append(record)
        return record

    def add_airline_record(self, company_name):
        record = Airline(company_name).to_dict()
        self.records["airlines"].append(record)
        return record

    def add_flight_record(self, client_id, airline_id, date, start_city, end_city):
        record = Flight(client_id, airline_id, date, start_city, end_city).to_dict()
        self.records["flights"].append(record)
        return record
