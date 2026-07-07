"""Flight record definition."""

FIELDS = (
    "Client_ID",
    "Airline_ID",
    "Date",
    "Start City",
    "End City",
)


def create_flight_record(client_id, airline_id, date, start_city, end_city):
    """Build a Flight record dict; the link IDs are coerced to int.

    ``date`` is stored as given -- use an ISO 8601 string, since JSON has no
    native date/time type.
    """
    return {
        "Client_ID": int(client_id),
        "Airline_ID": int(airline_id),
        "Date": date,
        "Start City": start_city,
        "End City": end_city,
    }


def is_flight_record(record):
    """Return ``True`` if ``record`` is a Flight record.

    Flights have no ``Type`` field, so they are identified by carrying both
    link IDs (``Client_ID`` and ``Airline_ID``).
    """
    return (
        isinstance(record, dict)
        and "Client_ID" in record
        and "Airline_ID" in record
    )
