"""JSONL persistence for records.

Records are stored as one JSON object per line (JSON Lines). The whole file is
the on-disk form of the shared ``records`` list. Loading returns a list of
dicts; saving overwrites the file with the current list.
"""

import os

import jsonlines

# Default location of the records file, resolved relative to this module so it
# works regardless of the current working directory.
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "record.jsonl")


def load_records(path=DEFAULT_PATH):
    """Load records from ``path`` and return them as a list of dicts.

    Returns an empty list if the file does not exist (first run) or is empty.
    """
    if not os.path.exists(path):
        return []

    records = []
    with jsonlines.open(path, mode="r") as reader:
        for record in reader:
            records.append(record)
    return records


def save_records(records, path=DEFAULT_PATH):
    """Write ``records`` (a list of dicts) to ``path`` as JSONL.

    The file is overwritten so its contents always match the in-memory list.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with jsonlines.open(path, mode="w") as writer:
        writer.write_all(records)
