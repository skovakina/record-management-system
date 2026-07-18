import os
import sys
import unittest
import tkinter as tk
import copy

# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)
import gui.app as app


class TestStore:
    SAMPLE_RECORDS = {
        "clients": [
            {
                "id": "11111111-1111-4111-8111-111111111111",
                "name": "Alice",
                "city": "London",
            },
            {
                "id": "22222222-2222-4222-8222-222222222222",
                "name": "Bob",
                "city": "Paris",
            },
        ],
        "airlines": [
            {
                "id": "33333333-3333-4333-8333-333333333333",
                "company_name": "SkyJet",
            },
            {
                "id": "44444444-4444-4444-8444-444444444444",
                "company_name": "AirWorld",
            },
        ],
        "flights": [
            {
                "client_id": "11111111-1111-4111-8111-111111111111",
                "airline_id": "33333333-3333-4333-8333-333333333333",
                "date": "2025-01-01T10:00",
            },
            {
                "client_id": "22222222-2222-4222-8222-222222222222",
                "airline_id": "44444444-4444-4444-8444-444444444444",
                "date": "2025-01-02T12:00",
            },
        ]
    }

    def __init__(self):
        self.records = copy.deepcopy(self.SAMPLE_RECORDS)
        self.deleted = []

    def delete_record(self, section, record):
        self.deleted.append((section, record))
        self.records[section].remove(record)


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



class TestRecordDisplayValues(unittest.TestCase):
    def test_show_record_sets_values(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "clients"
            instance._render_fields("clients")

            record = {
                "id": "11111111-1111-4111-8111-111111111111",
                "name": "Alice",
                "city": "London",
            }
            instance._show_record(record)

            self.assertEqual(instance.detail_entries["name"][1].get(), "Alice")
            self.assertEqual(instance.detail_entries["city"][1].get(), "London")
        finally:
            instance.destroy()

    def test_show_flight_record_uses_reference_display_names(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "flights"
            instance._render_fields("flights")

            instance._show_record(store.records["flights"][0])

            self.assertEqual(instance.detail_entries["client_id"][1].get(), "Alice")
            self.assertEqual(instance.detail_entries["airline_id"][1].get(), "SkyJet")
            self.assertEqual(instance.datetime_field.get(), "2025-01-01T10:00")
        finally:
            instance.destroy()




class TestRequiredValidation(unittest.TestCase):
    def test_validate_required_flags_missing_fields(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "clients"
            instance._render_fields("clients")

            instance.editing = True

            for _, (_, var, _) in instance.detail_entries.items():
                var.set("")

            instance._validate_required()

            self.assertTrue(instance.save_button.instate(["disabled"]))
        finally:
            instance.destroy()




class TestFieldState(unittest.TestCase):
    def test_field_state_logic(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "clients"

            self.assertEqual(instance._field_state("id", editing=True), "readonly")
            self.assertEqual(instance._field_state("name", editing=True), "normal")
            self.assertEqual(instance._field_state("name", editing=False), "readonly")
        finally:
            instance.destroy()

    def test_reference_field_state_logic(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "flights"
            instance._build_ref_index("flights")

            self.assertEqual(
                instance._field_state("client_id", editing=True), "readonly"
            )
            self.assertEqual(
                instance._field_state("client_id", editing=False), "disabled"
            )
        finally:
            instance.destroy()



class TestSorting(unittest.TestCase):
    def test_sorting_logic(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "clients"
            instance.current_records = store.records["clients"]

            instance.sort_field = "name"
            instance.sort_ascending = True
            sorted_records = instance._sorted(store.records["clients"])
            self.assertEqual(sorted_records[0]["name"], "Alice")

            instance.sort_ascending = False
            sorted_records_desc = instance._sorted(store.records["clients"])
            self.assertEqual(sorted_records_desc[0]["name"], "Bob")
        finally:
            instance.destroy()

    def test_on_sort_toggles_current_column(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.select_section("clients")
            self.assertEqual(instance.sort_field, "id")
            self.assertTrue(instance.sort_ascending)

            instance.on_sort("id")

            self.assertEqual(instance.sort_field, "id")
            self.assertFalse(instance.sort_ascending)
        finally:
            instance.destroy()



class TestSearchScheduling(unittest.TestCase):
    def test_search_scheduling(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "clients"
            instance.current_records = store.records["clients"]

            instance.search_var.set("Alice")
            instance._schedule_search()

            self.assertIsNotNone(instance._search_job)
        finally:
            if instance._search_job is not None:
                instance.after_cancel(instance._search_job)
            instance.destroy()

    def test_search_filters_flights_by_client_name(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.select_section("flights")
            instance._placeholder_active = False
            instance.search_var.set("bob")

            instance.on_search()

            self.assertEqual(instance.displayed_records, [store.records["flights"][1]])
        finally:
            instance.destroy()



class TestSectionSwitching(unittest.TestCase):
    def test_section_switching(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.select_section("clients")
            self.assertEqual(instance.current_section, "clients")
            self.assertEqual(instance.list_header.cget("text"), "Clients")
            self.assertEqual(instance.new_button.cget("text"), "New Client")

            instance.select_section("airlines")
            self.assertEqual(instance.current_section, "airlines")
            self.assertEqual(instance.list_header.cget("text"), "Airlines")
            self.assertEqual(instance.new_button.cget("text"), "New Airline")
        finally:
            instance.destroy()


class TestReferencesAndFormValues(unittest.TestCase):
    def test_build_ref_index_maps_names_to_ids(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance._build_ref_index("flights")

            self.assertEqual(
                instance.ref_index["client_id"]["to_id"]["Alice"],
                "11111111-1111-4111-8111-111111111111",
            )
            self.assertEqual(
                instance.ref_index["airline_id"]["to_display"][
                    "44444444-4444-4444-8444-444444444444"
                ],
                "AirWorld",
            )
        finally:
            instance.destroy()

    def test_form_values_converts_flight_dropdowns_to_ids(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "flights"
            instance._render_fields("flights")

            instance.detail_entries["client_id"][1].set("Alice")
            instance.detail_entries["airline_id"][1].set("AirWorld")
            instance.detail_entries["start_city"][1].set("London")
            instance.detail_entries["end_city"][1].set("Paris")
            instance.datetime_field.set("2025-03-04T09:15")

            self.assertEqual(
                instance._form_values(),
                {
                    "client_id": "11111111-1111-4111-8111-111111111111",
                    "airline_id": "44444444-4444-4444-8444-444444444444",
                    "date": "2025-03-04T09:15",
                    "start_city": "London",
                    "end_city": "Paris",
                },
            )
        finally:
            instance.destroy()

    def test_flight_dependents_finds_references(self):
        store = TestStore()
        instance = app.RecordManagerApp(store)
        try:
            instance.current_section = "clients"

            self.assertEqual(
                instance._flight_dependents(store.records["clients"][0]),
                [store.records["flights"][0]],
            )
        finally:
            instance.destroy()



class TestDateTimeField(unittest.TestCase):
    def test_datetime_field_get_set(self):
        root = tk.Tk()
        dt = app.DateTimeField(root)

        dt.set("2025-01-01T10:30")
        self.assertEqual(dt.get(), "2025-01-01T10:30")

        root.destroy()


if __name__ == "__main__":
    unittest.main()
