"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class Action(str, Enum):
    """Prescription action types."""
    RESCHEDULE = "RESCHEDULE"
    EXPEDITE = "EXPEDITE"
    PULL_SPARES = "PULL_SPARES"
    NO_ACTION = "NO_ACTION"


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    snowflake: Optional[str] = None


class ConfigResponse(BaseModel):
    """Configuration response (without secrets)."""
    snowflake: Dict[str, Any]
    app: Dict[str, Any]


class IngestRequest(BaseModel):
    """Data ingestion request."""
    data: List[Dict[str, Any]]
    format: str = Field(default="json", pattern="^(json|csv)$")


class IngestResponse(BaseModel):
    """Data ingestion response."""
    rows_ingested: int
    table: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FlightData(BaseModel):
    """Flight data model."""
    snapshot_ts: datetime
    icao24: str
    callsign: str
    origin_country: str
    time_position: Optional[float] = None
    last_contact: Optional[float] = None
    lon: float
    lat: float
    baro_altitude: Optional[float] = None
    on_ground: bool = False
    velocity: Optional[float] = None
    true_track: Optional[float] = None
    vertical_rate: Optional[float] = None
    geo_altitude: Optional[float] = None
    squawk: Optional[str] = None
    spi: Optional[bool] = None
    position_source: Optional[int] = None


class MachineData(BaseModel):
    """Machine data model."""
    machine_id: str
    type: str
    air_temp: float
    process_temp: float
    rotational_speed: float
    torque: float
    tool_wear: float
    failure_label: int
    event_ts: datetime


class ScoreRefreshResponse(BaseModel):
    """Score refresh response."""
    tables_refreshed: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PrescriptionData(BaseModel):
    """Prescription data model."""
    model_config = ConfigDict(from_attributes=True)
    
    job_id: str
    machine_id: str
    callsign: str
    frs: float = Field(ge=0, le=1)
    fls: float = Field(ge=0, le=1)
    otif_value: float
    expedite_cost: float
    downtime_cost: float
    roi: float
    action: Action
    explain_json: Dict[str, Any]
    timestamp: datetime


class PrescriptionResponse(BaseModel):
    """Prescription list response."""
    prescriptions: List[PrescriptionData]
    total: int
    page: int = 1
    page_size: int = 20


class WhatIfRequest(BaseModel):
    """What-if analysis request."""
    expedite_cost: float = Field(gt=0)
    downtime_cost: float = Field(gt=0)
    otif_value: float = Field(gt=0)
    frs: float = Field(ge=0, le=1)
    fls: float = Field(ge=0, le=1)


class WhatIfResponse(BaseModel):
    """What-if analysis response."""
    roi: float
    action: Action
    explanation: Dict[str, Any]
    inputs: WhatIfRequest
