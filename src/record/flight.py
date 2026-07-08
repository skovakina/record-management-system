"""Flight record definition."""

from dataclasses import asdict, dataclass


@dataclass
class Flight:
    client_id: int
    airline_id: int
    date: str
    start_city: str
    end_city: str

    def __post_init__(self):
        self.client_id = int(self.client_id)
        self.airline_id = int(self.airline_id)

    def to_dict(self):
        """Return this record as a plain dict, e.g. for JSONL persistence."""
        return asdict(self)
