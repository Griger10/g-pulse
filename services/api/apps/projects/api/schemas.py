from datetime import datetime
from typing import TypedDict, Annotated

from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    id: str
    owner_id: str
    name: str
    slug: str
    description: str
    created_at: datetime
    updated_at: datetime


class ProjectInfoCreate(BaseModel):
    name: str
    description: str | None


class ProjectInfoUpdate(BaseModel):
    name: str = None
    description: str | None = None


class ProjectSlugPath(TypedDict):
    slug: Annotated[str, Field(min_length=1)]


class ServiceInfo(BaseModel):
    id: str
    name: str
    url: str
    service_type: str
    check_interval: int = Field(gt=0)
    expected_status_code: int = Field(gt=0)
    current_status: str
    timeout: int = Field(gt=0)
    is_active: bool

    created_at: datetime
    updated_at: datetime


class ServiceInfoCreate(BaseModel):
    name: str
    url: str
    service_type: str
    check_interval: int = Field(gt=0)
    expected_status_code: int = Field(gt=0)
    timeout: int = Field(gt=0)
    is_active: bool


class ServiceInfoUpdate(BaseModel):
    name: str | None = None
    url: str | None = None
    service_type: str | None = None
    check_interval: int | None = Field(gt=0, default=None)
    expected_status_code: int | None = Field(gt=0, default=None)
    current_status: str | None = None
    timeout: int | None = Field(gt=0, default=None)
    is_active: bool | None = None


class ServiceIdPath(TypedDict):
    id: Annotated[str, Field(min_length=1)]


class ServiceCheckResponse(BaseModel):
    service_id: str
    result: str
    status_code: int = Field(gt=0)
    elapsed_time: int = Field(gt=0)
