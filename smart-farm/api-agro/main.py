"""
GreenRise AgroTech Smart Farm API.

REST API exposing read-only (GET) access to crop-zone sensor data,
compatible with Microsoft Foundry OpenAPI tool integration.
"""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

from data_store import get_zone, get_zones, load_farm
from models import CropSummary, ErrorResponse, Farm, MetricName, MetricReading, Zone

app = FastAPI(
    title="GreenRise AgroTech Smart Farm API",
    description=(
        "Read-only REST API for crop-zone sensor data (soil moisture, temperature, "
        "humidity and pH) at the Salinas Valley Demonstration Farm. "
        "Every resource can be queried for a single zone/metric or for all of them."
    ),
    version="1.0.0",
    servers=[{"url": "/", "description": "Current server"}],
)
app.openapi_version = "3.0.3"


@app.get("/swagger", include_in_schema=False)
def swagger_ui() -> HTMLResponse:
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=f"{app.title} - Swagger UI")


@app.get(
    "/farm",
    response_model=Farm,
    summary="Get full farm snapshot",
    description="Returns farm metadata and every crop zone with its readings and thresholds.",
    tags=["Farm"],
)
def get_full_farm() -> dict:
    return load_farm()


@app.get(
    "/zones",
    response_model=List[Zone],
    summary="List zones",
    description="Returns all crop zones, or a single zone when `zone_id` is provided.",
    tags=["Zones"],
    responses={404: {"model": ErrorResponse, "description": "Zone not found"}},
)
def list_zones(
    zone_id: Optional[str] = Query(
        default=None,
        description="Optional zone id to filter a single zone (e.g. ZONE-ALPHA). Omit to get all zones.",
    )
) -> list[dict]:
    if zone_id is None:
        return get_zones()
    zone = get_zone(zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found")
    return [zone]


@app.get(
    "/zones/{zone_id}",
    response_model=Zone,
    summary="Get a single zone",
    description="Returns the full record for one crop zone identified by `zone_id`.",
    tags=["Zones"],
    responses={404: {"model": ErrorResponse, "description": "Zone not found"}},
)
def get_single_zone(
    zone_id: str = Path(..., description="Zone identifier, e.g. ZONE-ALPHA")
) -> dict:
    zone = get_zone(zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found")
    return zone


@app.get(
    "/zones/{zone_id}/readings",
    response_model=List[MetricReading],
    summary="Get readings for a zone",
    description=(
        "Returns all sensor readings for a zone, or a single metric reading "
        "when `metric` is provided."
    ),
    tags=["Readings"],
    responses={404: {"model": ErrorResponse, "description": "Zone or metric not found"}},
)
def get_zone_readings(
    zone_id: str = Path(..., description="Zone identifier, e.g. ZONE-ALPHA"),
    metric: Optional[MetricName] = Query(
        default=None,
        description="Optional metric name to filter a single reading. Omit to get all readings.",
    ),
) -> list[dict]:
    zone = get_zone(zone_id)
    if zone is None:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found")

    readings = zone["readings"]
    if metric is not None:
        if metric.value not in readings:
            raise HTTPException(status_code=404, detail=f"Metric '{metric}' not found for zone '{zone_id}'")
        return [
            {
                "zone_id": zone["zone_id"],
                "metric": metric.value,
                "value": readings[metric.value]["value"],
                "unit": readings[metric.value]["unit"],
            }
        ]

    return [
        {
            "zone_id": zone["zone_id"],
            "metric": name,
            "value": reading["value"],
            "unit": reading["unit"],
        }
        for name, reading in readings.items()
        if name != "issues"
    ]


@app.get(
    "/crops",
    response_model=List[CropSummary],
    summary="List crops",
    description="Returns the crop grown in every zone, or a single zone's crop when `crop` is provided.",
    tags=["Crops"],
)
def list_crops(
    crop: Optional[str] = Query(
        default=None,
        description="Optional crop name (case-insensitive, partial match) to filter results. Omit to get all crops.",
    )
) -> list[dict]:
    zones = get_zones()
    if crop:
        crop_lower = crop.strip().lower()
        zones = [zone for zone in zones if crop_lower in zone["crop"].lower()]

    return [
        {"crop": zone["crop"], "zone_id": zone["zone_id"], "zone_name": zone["name"]}
        for zone in zones
    ]


def _flatten_nullable_anyof(node: object) -> object:
    """Convert Pydantic v2's OpenAPI 3.1-style `anyOf: [X, {type: null}]` into the
    OpenAPI 3.0-compatible `X` + `nullable: true`, recursively. OpenAPI 3.0 has no
    `type: null`, and leaving it in trips strict validators (e.g. Foundry OpenAPI tool)."""
    if isinstance(node, dict):
        any_of = node.get("anyOf")
        if isinstance(any_of, list) and any(item == {"type": "null"} for item in any_of):
            remaining = [item for item in any_of if item != {"type": "null"}]
            node = {k: v for k, v in node.items() if k != "anyOf"}
            if len(remaining) == 1:
                node.update(remaining[0])
            else:
                node["anyOf"] = remaining
            node["nullable"] = True
        return {key: _flatten_nullable_anyof(value) for key, value in node.items()}
    if isinstance(node, list):
        return [_flatten_nullable_anyof(item) for item in node]
    return node


def custom_openapi() -> dict:
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=app.servers,
        openapi_version=app.openapi_version,
    )
    schema = _flatten_nullable_anyof(schema)
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
