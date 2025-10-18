from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field


class ActionExecuteRequest(BaseModel):
    name: str
    params: Dict[str, Any] = Field(default_factory=dict)


class ActionExecuteResponse(BaseModel):
    name: str
    result: Dict[str, Any]
