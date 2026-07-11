"""Flight record definition."""

import uuid
from dataclasses import asdict, dataclass, field


@dataclass
class Flight:
    client_id: str
    airline_id: str
    date: str
    start_city: str
    end_city: str
    type: str = "flight"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        """Return this record as a plain dict, e.g. for JSONL persistence."""
        return asdict(self)
