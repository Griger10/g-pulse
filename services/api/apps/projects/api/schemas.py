from datetime import datetime
from typing import TypedDict, Annotated

from pydantic import BaseModel, Field


class ProjectInfo(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    created_at: datetime
    updated_at: datetime


class ProjectInfoCreate(BaseModel):
    name: str
    description: str | None


class ProjectsResponse(BaseModel):
    projects: list[ProjectInfo]


class ProjectDetailsPath(TypedDict):
    slug: Annotated[str, Field(min_length=1)]
