"""Read and write records from JSON."""

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

COLLECTION_PATHS = {
    "clients": os.path.join(DATA_DIR, "clients.json"),
    "airlines": os.path.join(DATA_DIR, "airlines.json"),
    "flights": os.path.join(DATA_DIR, "flights.json"),
}


def load_records(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def write_collection(records, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


def load_collections(paths=COLLECTION_PATHS):
    return {
        "clients": load_records(paths["clients"]),
        "airlines": load_records(paths["airlines"]),
        "flights": load_records(paths["flights"]),
    }


def save_collections(collections, paths=COLLECTION_PATHS):
    write_collection(collections["clients"], paths["clients"])
    write_collection(collections["airlines"], paths["airlines"])
    write_collection(collections["flights"], paths["flights"])
