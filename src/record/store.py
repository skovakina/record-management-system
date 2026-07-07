"""The shared records store.

Per the brief, all records live in a single list of dictionaries. ``RecordStore``
owns that list and knows how to load it from / save it to the JSONL file. Record
types (Client, Airline, Flight) add their records to this same shared list.
"""

from record import storage
from record.client import create_client_record


class RecordStore:
    """Holds the shared ``records`` list and its JSONL persistence."""

    def __init__(self, path=storage.DEFAULT_PATH):
        self.path = path
        # The shared list of record dictionaries (records: list = [{}, {}]).
        self.records = []

    def load(self):
        """Load records from disk into the shared list (called at startup)."""
        self.records = storage.load_records(self.path)
        return self.records

    def save(self):
        """Persist the shared list to disk (called when the app closes)."""
        storage.save_records(self.records, self.path)

    def add_client(self, id, name, **fields):
        """Create a Client record and append it to the shared list."""
        record = create_client_record(id, name, **fields)
        self.records.append(record)
        return record
