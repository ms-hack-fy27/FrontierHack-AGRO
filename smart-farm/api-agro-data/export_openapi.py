"""Utility to (re)generate the static openapi.json / openapi.yaml files from the FastAPI app."""

import json
from pathlib import Path

import yaml

from main import app

OUT_DIR = Path(__file__).resolve().parent


def main() -> None:
    schema = app.openapi()
    (OUT_DIR / "openapi.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    (OUT_DIR / "openapi.yaml").write_text(
        yaml.dump(schema, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    print("Wrote openapi.json and openapi.yaml")


if __name__ == "__main__":
    main()
