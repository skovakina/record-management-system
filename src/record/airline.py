"""Airline record definition.

An Airline record is a plain dictionary stored in the shared records list.
This module owns the canonical Airline field names and a factory function
that builds a well-formed Airline record dictionary.
"""

RECORD_TYPE = "Airline"

FIELDS = (
    "ID",
    "Type",
    "Company Name",
)


def create_airline_record(id, company_name):
    """Build an Airline record dictionary with all required fields.

    ``Type`` is set automatically to :data:`RECORD_TYPE`. ``id`` is coerced to
    ``int`` so records always carry a numeric identifier.
    """
    return {
        "ID": int(id),
        "Type": RECORD_TYPE,
        "Company Name": company_name,
    }


def is_airline_record(record):
    """Return ``True`` if ``record`` is an Airline record."""
    return isinstance(record, dict) and record.get("Type") == RECORD_TYPE