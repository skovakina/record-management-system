"""Client record definition."""

from dataclasses import asdict, dataclass


@dataclass
class Client:
    id: int
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

    def __post_init__(self):
        self.id = int(self.id)

    def to_dict(self):
        """Return this record as a plain dict, e.g. for JSONL persistence."""
        return asdict(self)
