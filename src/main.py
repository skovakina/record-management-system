from record.store import RecordStore


def main():
    store = RecordStore()
    store.load()

    print("Loaded records")


if __name__ == "__main__":
    main()
