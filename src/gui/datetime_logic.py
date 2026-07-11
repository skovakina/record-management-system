"""Pure date/time helpers for the DateTimeField widget.

No tkinter here, so this logic can be unit-tested without a display (the CI
runner is headless). DateTimeField wires these into its widgets.
"""

import calendar


def days_in_month(year, month):
    """Number of days in the given year/month; 31 if either is not a number."""
    if str(year).isdigit() and str(month).isdigit():
        return calendar.monthrange(int(year), int(month))[1]
    return 31


def valid_time_part(proposed, maximum):
    """Allow empty or a 1-2 digit number within 0..maximum (Entry key check)."""
    if proposed == "":
        return True
    if not proposed.isdigit() or len(proposed) > 2:
        return False
    return int(proposed) <= maximum


def assemble_iso(year, month, day, hour, minute):
    """Combine parts into 'YYYY-MM-DDTHH:MM', or None if incomplete/out of range."""
    if not (year and month and day and hour != "" and minute != ""):
        return None
    if int(hour) > 23 or int(minute) > 59:
        return None
    return (
        f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        f"T{int(hour):02d}:{int(minute):02d}"
    )


def split_iso(value):
    """Split an ISO 'YYYY-MM-DDTHH:MM' string into (year, month, day, hour, minute)."""
    date_part, _, time_part = str(value or "").partition("T")
    year, month, day = (date_part.split("-") + ["", "", ""])[:3]
    hour, minute = (time_part.split(":") + ["", ""])[:2]
    return year, month, day, hour, minute
