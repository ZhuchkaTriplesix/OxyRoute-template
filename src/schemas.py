from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str


class VersionResponse(BaseModel):
    name: str = "oxyroute-template"
    version: str = "0.1.0"


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
