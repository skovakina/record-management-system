from gui.app import RecordManagerApp
from record.store import RecordStore


def main():
    store = RecordStore()
    records = store.load()

    RecordManagerApp(records).mainloop()


if __name__ == "__main__":
    main()
