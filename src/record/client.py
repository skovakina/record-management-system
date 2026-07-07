"""Client record definition.

A Client record is a plain ``dict`` (per the brief, records are stored as a
list of dictionaries). This module owns the canonical Client field names and a
factory that builds a well-formed Client record dictionary.
"""

# The record ``Type`` value that identifies a Client record within the shared
# records list.
RECORD_TYPE = "Client"

# Canonical Client field names, in the order given by the brief. Kept as a
# single source of truth so the GUI, storage and tests all agree.
FIELDS = (
    "ID",
    "Type",
    "Name",
    "Address Line 1",
    "Address Line 2",
    "Address Line 3",
    "City",
    "State",
    "Zip Code",
    "Country",
    "Phone Number",
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
    """Build a Client record dictionary with all required fields.

    ``Type`` is set automatically to :data:`RECORD_TYPE`. ``id`` is coerced to
    ``int`` so records always carry a numeric identifier.
    """
    return {
        "ID": int(id),
        "Type": RECORD_TYPE,
        "Name": name,
        "Address Line 1": address_line_1,
        "Address Line 2": address_line_2,
        "Address Line 3": address_line_3,
        "City": city,
        "State": state,
        "Zip Code": zip_code,
        "Country": country,
        "Phone Number": phone_number,
    }


def is_client_record(record):
    """Return ``True`` if ``record`` is a Client record."""
    return isinstance(record, dict) and record.get("Type") == RECORD_TYPE
