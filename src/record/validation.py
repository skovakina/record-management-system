"""Validation rules for records — the single source of truth.

Kept in the data layer (not the GUI) so the window and RecordStore share one
set of rules instead of each keeping its own copy, which would drift apart.
Field names are the record data keys (snake_case), matching the record.*
dataclasses.
"""

# Required (non-empty) fields per record type. ``id`` and ``type`` are
# system-assigned, so they are never user-required.
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


def missing_fields(record_type, data):
    """Return the required fields that are empty or blank in ``data``."""
    return [
        field
        for field in REQUIRED.get(record_type, [])
        if str(data.get(field, "")).strip() == ""
    ]


def reference_errors(data, records):
    """Return a Flight's reference fields that don't point at an existing record.

    Only applies to Flight data; empty references are left to the required
    check. ``records`` is the shared list of record dicts.
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


def validate(record_type, data, records=None):
    """Return ``{field: reason}`` for every invalid field; empty dict == valid.

    Checks required (non-empty) fields always, and unknown references when the
    shared ``records`` list is supplied (e.g. at the data layer on add).
    """
    errors = {field: "required" for field in missing_fields(record_type, data)}
    if records is not None:
        for field in reference_errors(data, records):
            errors.setdefault(field, "unknown reference")
    return errors
