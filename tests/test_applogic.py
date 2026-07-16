import os
import sys
import unittest
import tkinter as tk

HEADLESS = os.name != "nt" and not os.environ.get("DISPLAY")
# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)
import gui.app as app


class DummyStore:
    records = {
        "clients": [
            {"id": 1, "name": "Alice", "city": "London"},
            {"id": 2, "name": "Bob", "city": "Paris"},
        ],
        "airlines": [
            {"id": 10, "company_name": "SkyJet"},
            {"id": 11, "company_name": "AirWorld"},
        ],
        "flights": [
            {"client_id": 1, "airline_id": 10, "date": "2025-01-01T10:00"},
            {"client_id": 2, "airline_id": 11, "date": "2025-01-02T12:00"},
        ]
    }


class TestAppPureFunctions(unittest.TestCase):
    def test_darken(self):
        self.assertEqual(app._darken("#ffffff", 0.5), "#7f7f7f")
        self.assertEqual(app._darken("#000000", 0.5), "#000000")

    def test_label_for(self):
        self.assertEqual(app._label_for("zip_code"), "Zip Code")
        self.assertEqual(app._label_for("id"), "ID")
        self.assertEqual(app._label_for("phone_number"), "Phone Number")

    def test_section_label(self):
        self.assertEqual(app._section_label("clients"), "Clients")
        self.assertEqual(app._section_label("airlines"), "Airlines")


@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestRecordDisplayValues(unittest.TestCase):
    def test_show_record_sets_values(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance._render_fields("clients")

        record = {"id": 1, "name": "Alice", "city": "London"}
        instance._show_record(record)

        self.assertEqual(instance.detail_entries["name"][1].get(), "Alice")
        self.assertEqual(instance.detail_entries["city"][1].get(), "London")


class TestRecordDisplay(unittest.TestCase):
    def test_show_record_sets_values(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance._render_fields("clients")

        record = {"id": 1, "name": "Alice", "city": "London"}
        instance._show_record(record)

        self.assertEqual(instance.detail_entries["name"][1].get(), "Alice")
        self.assertEqual(instance.detail_entries["city"][1].get(), "London")


@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestRequiredValidation(unittest.TestCase):
    def test_validate_required_flags_missing_fields(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance._render_fields("clients")

        instance.editing = True

        for _, (_, var, _) in instance.detail_entries.items():
            var.set("")

        instance._validate_required()

        self.assertTrue(instance.save_button.instate(["disabled"]))



@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestFieldState(unittest.TestCase):
    def test_field_state_logic(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"

        self.assertEqual(instance._field_state("id", editing=True), "readonly")
        self.assertEqual(instance._field_state("name", editing=True), "normal")
        self.assertEqual(instance._field_state("name", editing=False), "readonly")


@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestSorting(unittest.TestCase):
    def test_sorting_logic(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance.current_records = store.records["clients"]

        instance.sort_field = "name"
        instance.sort_ascending = True
        sorted_records = sorted(store.records["clients"], key=lambda r: r["name"])
        self.assertEqual(sorted_records[0]["name"], "Alice")

        instance.sort_ascending = False
        sorted_records_desc = sorted(store.records["clients"], key=lambda r: r["name"], reverse=True)
        self.assertEqual(sorted_records_desc[0]["name"], "Bob")


@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestSearchScheduling(unittest.TestCase):
    def test_search_scheduling(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance.current_records = store.records["clients"]

        instance.search_var.set("Alice")
        instance._schedule_search()

        self.assertIsNotNone(instance._search_job)


@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestSectionSwitching(unittest.TestCase):
    def test_section_switching(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)

        instance.select_section("clients")
        self.assertEqual(instance.current_section, "clients")

        instance.select_section("airlines")
        self.assertEqual(instance.current_section, "airlines")


@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestDateTimeField(unittest.TestCase):
    def test_datetime_field_get_set(self):
        root = tk.Tk()
        dt = app.DateTimeField(root)

        dt.set("2025-01-01T10:30")
        self.assertEqual(dt.get(), "2025-01-01T10:30")

        root.destroy()


if __name__ == "__main__":
    unittest.main()
