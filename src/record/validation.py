"""Validation rules shared by the GUI and RecordStore.

Kept in the data layer so both use one set of rules. Field names are the
record data keys (snake_case), matching the record.* dataclasses.
"""

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


def missing_fields(record_type, data):
    """Return the required fields that are empty or blank."""
    return [
        field
        for field in REQUIRED.get(record_type, [])
        if str(data.get(field, "")).strip() == ""
    ]


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


def validate(record_type, data, records=None):
    """Return {field: reason} for every invalid field; empty dict means valid.

    Always checks required fields; also checks references when records is given.
    """
    errors = {field: "required" for field in missing_fields(record_type, data)}
    if records is not None:
        for field in reference_errors(data, records):
            errors.setdefault(field, "unknown reference")
    return errors
