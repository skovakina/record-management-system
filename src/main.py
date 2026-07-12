from gui.app import RecordManagerApp
from record.store import RecordStore


def main():
    store = RecordStore()
    store.load_records()

    RecordManagerApp(store).mainloop()


if __name__ == "__main__":
    main()
