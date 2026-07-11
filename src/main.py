"""Application entry point: load records, launch the GUI, save on shutdown."""

from gui.app import RecordManagerApp
from record.store import RecordStore


def main():
    store = RecordStore()
    store.load()
    print(f"Loaded {len(store.records)} record(s) from {store.path}")

    # TODO: pass `store` into the GUI so create/update/delete/search operate on
    # it, and have the window's on_close call store.save(). For now the GUI runs
    # on its in-memory list; wiring persistence is tracked separately (#7/#8).
    RecordManagerApp().mainloop()

    store.save()


if __name__ == "__main__":
    main()
