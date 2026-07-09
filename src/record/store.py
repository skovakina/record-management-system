"""The shared records store: one list of record dicts, persisted as JSONL."""

from record import storage
from record.client import Client
from record.airline import Airline
from record.flight import Flight



class RecordStore:

    def __init__(self, path=storage.DEFAULT_PATH):
        self.path = path
        self.records = []

    def load(self):
        """Load records from disk into the shared list."""
        self.records = storage.load_records(self.path)
        return self.records

    def save(self):
        """Persist the shared list to disk."""
        storage.save_records(self.records, self.path)

    def add_client(self, id, name, **fields):
        """Create a Client record and append it to the shared list."""
        record = Client(id, name, **fields).to_dict()
        self.records.append(record)
        return record

    def add_airline(self, id, company_name):
        """Create an Airline record and append it to the shared list."""
        record = Airline(id, company_name).to_dict()
        self.records.append(record)
        return record

    def add_flight(self, client_id, airline_id, date, start_city, end_city):
        """Create a Flight record and append it to the shared list."""
        record = Flight(client_id, airline_id, date, start_city, end_city).to_dict()
        self.records.append(record)
        return record
