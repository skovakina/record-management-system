"""JSON loading and saving for the client, airline, and flight collections."""

import json
import os

DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "data")
)

COLLECTION_TYPES = {
    "clients": "client",
    "airlines": "airline",
    "flights": "flight",
}

DEFAULT_COLLECTION_PATHS = {
    "clients": os.path.join(DATA_DIR, "clients.json"),
    "airlines": os.path.join(DATA_DIR, "airlines.json"),
    "flights": os.path.join(DATA_DIR, "flights.json"),
}


def load_records(path):
    """Load records from a JSON file."""
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def save_records(records, path):
    """Save records to a JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


def load_collections(paths=None):
    """Load all collections into a dictionary keyed by collection name."""
    if paths is None:
        paths = DEFAULT_COLLECTION_PATHS

    return {
        "clients": load_records(paths["clients"]),
        "airlines": load_records(paths["airlines"]),
        "flights": load_records(paths["flights"]),
    }


def save_collections(collections, paths=None):
    """Save all collections to their JSON files."""
    if paths is None:
        paths = DEFAULT_COLLECTION_PATHS

    save_records(collections["clients"], paths["clients"])
    save_records(collections["airlines"], paths["airlines"])
    save_records(collections["flights"], paths["flights"])
