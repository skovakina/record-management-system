"""Application entry point.

On startup the shared records list is loaded from the JSONL file (or created
empty on first run). On shutdown the list is saved back to disk.
"""

from record.store import RecordStore


def main():
    store = RecordStore()
    store.load()  # Check for existing records and load them at startup.
    print(f"Loaded {len(store.records)} record(s) from {store.path}")

    # The GUI will drive create/update/delete/search against ``store`` here.

    store.save()  # Persist the shared list when the application closes.


if __name__ == "__main__":
    main()
