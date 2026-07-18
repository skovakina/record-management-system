import os
import sys
import unittest
import tkinter as tk

# Make src importable when running "python -m unittest" from the repo root.
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), os.pardir, "src"),
)

import gui.app as app


def _has_display():
    """
    Probe for a usable Tk display instead of guessing from os.name/DISPLAY.

    The old check (`os.name != "nt" and not os.environ.get("DISPLAY")`) was
    wrong on both platforms it tried to special-case:

    - Windows never sets DISPLAY, so `os.name != "nt"` short-circuited the
      check to False -> GUI tests always attempted to run, even headless CI.

    - macOS doesn't use the DISPLAY env var for its native Tk backend, so the
      check always evaluated to True -> GUI tests were always skipped, even
      with a real display available.

    Actually trying to create (and immediately destroy) a Tk root is the only
    reliable cross-platform way to tell.
    """
    try:
        root = tk.Tk()
        root.destroy()
        return True
    except tk.TclError:
        return False


HEADLESS = not _has_display()

# UUIDs below follow the app's real schema (version-4 style strings)
# rather than throwaway ints, so fixtures match what the app actually
# stores/looks up.
CLIENT_1_ID = "11111111-1111-4111-8111-111111111111"
CLIENT_2_ID = "22222222-2222-4222-8222-222222222222"
AIRLINE_1_ID = "33333333-3333-4333-8333-333333333333"
AIRLINE_2_ID = "44444444-4444-4444-8444-444444444444"


class DummyStore:
    records = {
        "clients": [
            {
                "id": CLIENT_1_ID,
                "name": "Alice",
                "city": "London",
            },
            {
                "id": CLIENT_2_ID,
                "name": "Bob",
                "city": "Paris",
            },
        ],
        "airlines": [
            {
                "id": AIRLINE_1_ID,
                "company_name": "SkyJet",
            },
            {
                "id": AIRLINE_2_ID,
                "company_name": "AirWorld",
            },
        ],
        "flights": [
            {
                "client_id": CLIENT_1_ID,
                "airline_id": AIRLINE_1_ID,
                "date": "2025-01-01T10:00",
            },
            {
                "client_id": CLIENT_2_ID,
                "airline_id": AIRLINE_2_ID,
                "date": "2025-01-02T12:00",
            },
        ],
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

        record = {
            "id": CLIENT_1_ID,
            "name": "Alice",
            "city": "London",
        }

        instance._show_record(record)

        self.assertEqual(
            instance.detail_entries["name"][1].get(),
            "Alice",
        )
        self.assertEqual(
            instance.detail_entries["city"][1].get(),
            "London",
        )


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

        self.assertEqual(
            instance._field_state("id", editing=True),
            "readonly",
        )
        self.assertEqual(
            instance._field_state("name", editing=True),
            "normal",
        )
        self.assertEqual(
            instance._field_state("name", editing=False),
            "readonly",
        )


@unittest.skipIf(HEADLESS, "Tkinter GUI tests require a display")
class TestSorting(unittest.TestCase):

    def test_sorting_logic(self):
        """
        Exercises the app's own _sorted() method (case-insensitive sort by
        the active sort_field/sort_ascending), rather than re-testing
        Python's built-in sorted().
        """
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance.current_records = store.records["clients"]

        instance.sort_field = "name"
        instance.sort_ascending = True

        ascending = instance._sorted(store.records["clients"])
        self.assertEqual(
            [r["name"] for r in ascending],
            ["Alice", "Bob"],
        )

        instance.sort_ascending = False

        descending = instance._sorted(store.records["clients"])
        self.assertEqual(
            [r["name"] for r in descending],
            ["Bob", "Alice"],
        )

    def test_sorting_is_case_insensitive(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance.sort_field = "name"
        instance.sort_ascending = True

        mixed_case = [
            {
                "id": CLIENT_1_ID,
                "name": "bob",
                "city": "Paris",
            },
            {
                "id": CLIENT_2_ID,
                "name": "Alice",
                "city": "London",
            },
        ]

        result = instance._sorted(mixed_case)

        self.assertEqual(
            [r["name"] for r in result],
            ["Alice", "bob"],
        )

    def test_on_sort_toggles_direction_then_switches_field(self):
        store = DummyStore()
        instance = app.RecordManagerApp(store)
        instance.current_section = "clients"
        instance.current_records = store.records["clients"]
        instance.sort_field = "name"
        instance.sort_ascending = True

        instance.on_sort("name")
        self.assertEqual(instance.sort_field, "name")
        self.assertFalse(instance.sort_ascending)

        instance.on_sort("id")
        self.assertEqual(instance.sort_field, "id")
        self.assertTrue(instance.sort_ascending)


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

        self.assertEqual(
            dt.get(),
            "2025-01-01T10:30",
        )

        root.destroy()


if __name__ == "__main__":
    unittest.main()
