"""Flight record definition.

A Flight record is a plain ``dict`` (per the brief, records are stored as a
list of dictionaries). This module owns the canonical Flight field names and a
factory that builds a well-formed Flight record dictionary.

Note: unlike Client and Airline records, the brief does not give Flight a
``Type`` field, so one is not added here. Flight records are recognised by
their structure (see :func:`is_flight_record`). Dates are stored as strings
(ISO 8601 recommended) because JSON has no native date/time type.
"""

# Canonical Flight field names, in the order given by the brief. Kept as a
# single source of truth so the GUI, storage and tests all agree.
FIELDS = (
    "Client_ID",
    "Airline_ID",
    "Date",
    "Start City",
    "End City",
)


def create_flight_record(client_id, airline_id, date, start_city, end_city):
    """Build a Flight record dictionary with all required fields.

    ``client_id`` and ``airline_id`` are coerced to ``int`` so records always
    carry numeric identifiers linking to the Client and Airline records.
    ``date`` is stored as given (use an ISO 8601 string for JSONL round-trips).
    """
    return {
        "Client_ID": int(client_id),
        "Airline_ID": int(airline_id),
        "Date": date,
        "Start City": start_city,
        "End City": end_city,
    }


def is_flight_record(record):
    """Return ``True`` if ``record`` looks like a Flight record.

    Flight records have no ``Type`` field, so they are identified by carrying
    both link fields (``Client_ID`` and ``Airline_ID``).
    """
    return (
        isinstance(record, dict)
        and "Client_ID" in record
        and "Airline_ID" in record
    )
