"""Airline record definition."""

import uuid
from dataclasses import asdict, dataclass, field


@dataclass
class Airline:
    company_name: str
    type: str = "airline"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


    def to_dict(self):
        """Return this record as a plain dict, e.g. for JSONL persistence."""
        return asdict(self)
