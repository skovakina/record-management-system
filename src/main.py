"""Application entry point: launch the Record Management System GUI."""

from gui.app import RecordManagerApp


def main():
    RecordManagerApp().mainloop()


if __name__ == "__main__":
    main()
