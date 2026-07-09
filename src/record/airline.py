"""Airline record definition."""

from dataclasses import asdict, dataclass


@dataclass
class Airline:
    id: int
    company_name: str
    type: str = "airline"

    def __post_init__(self):
        self.id = int(self.id)

    def to_dict(self):
        """Return this record as a plain dict, e.g. for JSONL persistence."""
        return asdict(self)
