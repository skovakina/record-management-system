"""Unit tests for gui.datetime_logic — the pure date/time helpers (no tkinter)."""

import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), os.pardir, "src")
)

from gui.datetime_logic import (
    assemble_iso,
    days_in_month,
    split_iso,
    valid_time_part,
)


class TestDaysInMonth(unittest.TestCase):
    def test_february_non_leap(self):
        self.assertEqual(days_in_month("2026", "02"), 28)

    def test_february_leap_year(self):
        self.assertEqual(days_in_month("2024", "02"), 29)

    def test_thirty_day_month(self):
        self.assertEqual(days_in_month("2026", "04"), 30)

    def test_unknown_parts_default_to_31(self):
        self.assertEqual(days_in_month("", ""), 31)
        self.assertEqual(days_in_month("2026", ""), 31)


class TestValidTimePart(unittest.TestCase):
    def test_empty_allowed(self):
        self.assertTrue(valid_time_part("", 23))

    def test_in_range(self):
        self.assertTrue(valid_time_part("23", 23))
        self.assertTrue(valid_time_part("0", 59))

    def test_out_of_range_rejected(self):
        self.assertFalse(valid_time_part("24", 23))
        self.assertFalse(valid_time_part("60", 59))

    def test_non_digit_or_too_long_rejected(self):
        self.assertFalse(valid_time_part("9a", 23))
        self.assertFalse(valid_time_part("123", 59))


class TestAssembleIso(unittest.TestCase):
    def test_complete_parts(self):
        self.assertEqual(
            assemble_iso("2026", "7", "9", "9", "5"), "2026-07-09T09:05"
        )

    def test_incomplete_returns_none(self):
        self.assertIsNone(assemble_iso("2026", "07", "", "09", "00"))
        self.assertIsNone(assemble_iso("2026", "07", "09", "", ""))

    def test_out_of_range_returns_none(self):
        self.assertIsNone(assemble_iso("2026", "07", "09", "24", "00"))
        self.assertIsNone(assemble_iso("2026", "07", "09", "10", "60"))


class TestSplitIso(unittest.TestCase):
    def test_round_trip_with_assemble(self):
        iso = "2026-07-09T14:30"
        self.assertEqual(assemble_iso(*split_iso(iso)), iso)

    def test_empty_value_gives_blanks(self):
        self.assertEqual(split_iso(""), ("", "", "", "", ""))
        self.assertEqual(split_iso(None), ("", "", "", "", ""))


if __name__ == "__main__":
    unittest.main()
