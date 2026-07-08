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


def _validate_id(id):
    """Return ``id`` as a non-negative int, or raise ``ValueError``."""
    # int(True) would silently become 1, so reject bool before int().
    if isinstance(id, bool):
        raise ValueError(f"Client ID must be an integer, got {id!r}")
    try:
        client_id = int(id)
    except (TypeError, ValueError):
        raise ValueError(f"Client ID must be an integer, got {id!r}")
    if client_id < 0:
        raise ValueError(f"Client ID must be non-negative, got {client_id}")
    return client_id


def _validate_name(name):
    """Return the stripped ``name``, or raise ``ValueError`` if empty."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Client name is required and cannot be empty")
    return name.strip()


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
    """Build a validated Client record dict with all fields from the brief."""
    return {
        "id": _validate_id(id),
        "type": RECORD_TYPE,
        "name": _validate_name(name),
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
