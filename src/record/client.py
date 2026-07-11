"""Client record definition."""

import uuid
from dataclasses import asdict, dataclass, field


@dataclass
class Client:
    name: str
    address_line_1: str = ""
    address_line_2: str = ""
    address_line_3: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = ""
    phone_number: str = ""
    type: str = "client"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


    def to_dict(self):
        """Return this record as a plain dict, e.g. for JSONL persistence."""
        return asdict(self)
