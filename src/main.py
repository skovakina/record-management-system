"""Application entry point: load records on startup, save on shutdown."""

from record.store import RecordStore


def main():
    store = RecordStore()
    store.load()
    print(f"Loaded {len(store.records)} record(s) from {store.path}")

    # The GUI will drive create/update/delete/search against the store here.

    store.save()


if __name__ == "__main__":
    main()
