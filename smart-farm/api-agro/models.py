"""Pydantic schemas for the GreenRise AgriTech Smart Farm API."""

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field


class MetricName(str, Enum):
    soil_moisture = "soil_moisture"
    temperature = "temperature"
    humidity = "humidity"
    ph_level = "ph_level"


class ZoneStatus(str, Enum):
    normal = "normal"
    warning = "warning"
    critical = "critical"


class Reading(BaseModel):
    value: float = Field(..., description="Current sensor reading value.")
    unit: str = Field(..., description="Unit of measure for the reading.")


class SensorReadings(BaseModel):
    soil_moisture: Reading = Field(..., description="Latest soil moisture reading.")
    temperature: Reading = Field(..., description="Latest temperature reading.")
    humidity: Reading = Field(..., description="Latest humidity reading.")
    ph_level: Reading = Field(..., description="Latest pH reading.")
    issues: List[str] = Field(..., description="Known pests, diseases, or other observed issues in the zone.")


class Threshold(BaseModel):
    min: float = Field(..., description="Minimum acceptable value.")
    max: float = Field(..., description="Maximum acceptable value.")


class Zone(BaseModel):
    zone_id: str = Field(..., description="Unique identifier of the crop zone.")
    name: str = Field(..., description="Human readable zone name.")
    crop: str = Field(..., description="Crop planted in the zone.")
    status: ZoneStatus = Field(..., description="Overall health status of the zone.")
    last_inspection: str = Field(..., description="Date of the last manual inspection (YYYY-MM-DD).")
    readings: SensorReadings = Field(..., description="Latest sensor readings and observed issues for the zone.")
    thresholds: Dict[str, Threshold] = Field(..., description="Acceptable ranges for each sensor metric.")


class Farm(BaseModel):
    farm: str = Field(..., description="Farm name.")
    site: str = Field(..., description="Site/demonstration location name.")
    timestamp: str = Field(..., description="ISO-8601 timestamp of the data snapshot.")
    zones: List[Zone] = Field(..., description="All crop zones monitored on the farm.")


class MetricReading(BaseModel):
    zone_id: str = Field(..., description="Zone the reading belongs to.")
    metric: MetricName = Field(..., description="Metric name.")
    value: float = Field(..., description="Metric value.")
    unit: str = Field(..., description="Unit of measure.")


class CropSummary(BaseModel):
    crop: str = Field(..., description="Crop name.")
    zone_id: str = Field(..., description="Zone growing this crop.")
    zone_name: str = Field(..., description="Zone display name.")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human readable error message.")
