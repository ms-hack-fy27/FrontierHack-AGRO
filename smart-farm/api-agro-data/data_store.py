"""Loads and caches the smart farm sensor dataset."""

import json
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "smart_farm_data.json"


@lru_cache(maxsize=1)
def load_farm() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as data_file:
        return json.load(data_file)


def get_zones() -> list[dict]:
    return load_farm()["zones"]


def get_zone(zone_id: str) -> dict | None:
    zone_id_lower = zone_id.strip().lower()
    return next(
        (zone for zone in get_zones() if zone["zone_id"].lower() == zone_id_lower),
        None,
    )
