from gui.app import RecordManagerApp
from record.store import RecordStore


def main():
    store = RecordStore()
<<<<<<< HEAD
    store.load_records()
    
    print("Loaded records")
    
    RecordManagerApp().mainloop()
=======
    records = store.load()

    RecordManagerApp(records).mainloop()
>>>>>>> e69420f (connect with ui)


if __name__ == "__main__":
    main()
