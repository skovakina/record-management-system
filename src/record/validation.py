"""Validation rules shared by the GUI and RecordStore.

Kept in the data layer so both use one set of rules. Field names are the
record data keys (snake_case), matching the record.* dataclasses.
"""

import re

# Required non-empty fields per type; id and type are system-assigned.
REQUIRED = {
    "client": [
        "name",
        "address_line_1",
        "city",
        "state",
        "zip_code",
        "country",
        "phone_number",
    ],
    "airline": ["company_name"],
    "flight": ["client_id", "airline_id", "date", "start_city", "end_city"],
}

# Phone format: digits plus the common separators + - ( ) and space. 7 to 15 digits.
_PHONE_ALLOWED = re.compile(r"^[0-9+()\-\s]+$")
_PHONE_MIN_DIGITS = 7
_PHONE_MAX_DIGITS = 15


def _norm(value):
    # Normalise a value for comparison.
    return str(value).strip().casefold()


def missing_fields(record_type, data):
    """Return the required fields that are empty or blank."""
    return [
        field
        for field in REQUIRED.get(record_type, [])
        if str(data.get(field, "")).strip() == ""
    ]


def _phone_ok(value):
    text = str(value).strip()
    if not _PHONE_ALLOWED.match(text):
        return False
    digits = sum(character.isdigit() for character in text)
    return _PHONE_MIN_DIGITS <= digits <= _PHONE_MAX_DIGITS


def format_errors(record_type, data):
    # Return field-reason for present values with an invalid format.
    errors = {}
    if record_type == "client":
        phone = str(data.get("phone_number", "")).strip()
        if phone and not _phone_ok(phone):
            errors["phone_number"] = "invalid format"
    return errors


def logic_errors(record_type, data):
    # Return field-reason for values that break a cross-field rule.
    errors = {}
    if record_type == "flight":
        start = _norm(data.get("start_city", ""))
        end = _norm(data.get("end_city", ""))
        if start and end and start == end:
            errors["start_city"] = "same as end city"
            errors["end_city"] = "same as start city"
    return errors


def duplicate_errors(record_type, data, records, exclude_id=None):
    # Return reason for duplicate values.
    if record_type != "airline":
        return {}
    name = _norm(data.get("company_name", ""))
    if not name:
        return {}
    others = (record for record in records if record.get("id") != exclude_id)
    if any(
        other.get("type") == "airline" and _norm(other.get("company_name", "")) == name
        for other in others
    ):
        return {"company_name": "duplicate"}
    return {}


def reference_errors(data, records):
    """Return Flight reference fields that don't point at an existing record.

    Flights only; empty references are left to the required check.
    """
    if data.get("type") != "flight" and "client_id" not in data:
        return []
    client_ids = {r.get("id") for r in records if r.get("type") == "client"}
    airline_ids = {r.get("id") for r in records if r.get("type") == "airline"}
    errors = []
    if data.get("client_id") and data["client_id"] not in client_ids:
        errors.append("client_id")
    if data.get("airline_id") and data["airline_id"] not in airline_ids:
        errors.append("airline_id")
    return errors


def validate(record_type, data, records=None, exclude_id=None):
    """Return {field: reason} for every invalid field; empty dict means valid.

    Always checks required fields, value formats, and cross-field logic. When
    records is given, also checks flight references and airline-name uniqueness.
    """
    errors = {field: "required" for field in missing_fields(record_type, data)}
    for field, reason in format_errors(record_type, data).items():
        errors.setdefault(field, reason)
    for field, reason in logic_errors(record_type, data).items():
        errors.setdefault(field, reason)
    if records is not None:
        for field in reference_errors(data, records):
            errors.setdefault(field, "unknown reference")
        for field, reason in duplicate_errors(
            record_type, data, records, exclude_id
        ).items():
            errors.setdefault(field, reason)
    return errors
