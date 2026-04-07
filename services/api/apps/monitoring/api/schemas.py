from datetime import datetime
from typing import TypedDict, Annotated

from pydantic import BaseModel, Field


class HealthCheckInfo(BaseModel):
    id: str
    service_id: str
    result: str
    status_code: int | None
    response_time_ms: int
    error_message: str
    checked_at: datetime


class HealthChecksResponse(BaseModel):
    checks: list[HealthCheckInfo]
    total: int
    page: int
    page_size: int


class UptimeResponse(BaseModel):
    service_id: str
    period: str
    uptime_percent: float
    avg_response_time_ms: int
    min_response_time_ms: int
    max_response_time_ms: int
    total_checks: int


class ServiceStatusInfo(BaseModel):
    id: str
    name: str
    current_status: str
    uptime_24h_percent: float
    avg_response_time_ms: int


class ProjectStatusResponse(BaseModel):
    project_name: str
    project_slug: str
    services: list[ServiceStatusInfo]


class ServiceIdPath(TypedDict):
    id: str


class ProjectSlugPath(TypedDict):
    slug: str
