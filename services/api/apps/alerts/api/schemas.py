from datetime import datetime
from typing import TypedDict

from pydantic import BaseModel, Field


class AlertRuleInfo(BaseModel):
    id: str
    service_id: str
    condition: str
    threshold: int
    transport: str
    is_active: bool
    cooldown_minutes: int
    created_at: datetime


class AlertRuleCreate(BaseModel):
    condition: str
    threshold: int = Field(gt=0, default=3)
    transport: str
    cooldown_minutes: int = Field(gt=0, default=5)
    is_active: bool = True


class AlertRuleUpdate(BaseModel):
    condition: str | None = None
    threshold: int | None = Field(gt=0, default=None)
    transport: str | None = None
    cooldown_minutes: int | None = Field(gt=0, default=None)
    is_active: bool | None = None


class AlertEventInfo(BaseModel):
    id: str
    rule_id: str
    service_id: str
    status: str
    message: str
    created_at: datetime


class AlertEventsResponse(BaseModel):
    events: list[AlertEventInfo]
    total: int
    page: int
    page_size: int


class ServiceIdPath(TypedDict):
    id: str


class AlertRuleIdPath(TypedDict):
    id: str
