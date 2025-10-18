from __future__ import annotations

from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None


class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class ChatOptions(BaseModel):
    model: Optional[str] = None
    temperature: float = 0.2
    lang: str = "ar"


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    options: ChatOptions = Field(default_factory=ChatOptions)


class ChatStreamChunk(BaseModel):
    type: Literal["message", "tool_call", "tool_result", "error", "done"]
    delta: Optional[str] = None
    tool_name: Optional[str] = None
    tool_arguments: Optional[dict[str, Any]] = None
    tool_result: Optional[dict[str, Any]] = None
    message_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: ChatMessage
    latency_ms: int


class Suggestion(BaseModel):
    title: str
    body: str
    action: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
