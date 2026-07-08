"""Client record definition and validation."""

RECORD_TYPE = "Client"

FIELDS = (
    "id",
    "type",
    "name",
    "address_line_1",
    "address_line_2",
    "address_line_3",
    "city",
    "state",
    "zip_code",
    "country",
    "phone_number",
)


def create_client_record(
    id,
    name,
    address_line_1="",
    address_line_2="",
    address_line_3="",
    city="",
    state="",
    zip_code="",
    country="",
    phone_number="",
):
    """Build a Client record dict with all fields from the brief.

    The caller supplies a valid ID (assigned by RecordStore); the factory just
    assembles the record.
    """
    return {
        "id": int(id),
        "type": RECORD_TYPE,
        "name": name,
        "address_line_1": address_line_1,
        "address_line_2": address_line_2,
        "address_line_3": address_line_3,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": country,
        "phone_number": phone_number,
    }


def is_client_record(record):
    """Return ``True`` if ``record`` is a Client record."""
    return isinstance(record, dict) and record.get("type") == RECORD_TYPE
