from __future__ import annotations

import json
import time
import uuid
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.schemas.chat import ChatMessage, ChatRequest, ChatResponse, ChatStreamChunk
from backend.app.ai.services.llm import llm_client
from backend.app.ai.services.rag import gather_context_chunks
from backend.app.ai.services.tools import registry
from backend.app.api.deps import User, ensure_rate_limit
from backend.app.db.database import get_session
from backend.app.db.models import AIInteraction

router = APIRouter()


async def _log_interaction(
    session: AsyncSession,
    user: User,
    role: str,
    content: str,
    tool_name: Optional[str] = None,
    latency_ms: Optional[int] = None,
) -> None:
    record = AIInteraction(
        user_id=user.id,
        role=role,
        content=content,
        tool_name=tool_name,
        latency_ms=latency_ms,
    )
    session.add(record)
    await session.flush()


def _to_openai_messages(messages: List[ChatMessage]) -> List[Dict[str, str]]:
    converted: List[Dict[str, str]] = []
    for message in messages:
        converted.append({
            "role": message.role,
            "content": message.content,
            **({"name": message.name} if message.name else {}),
        })
    return converted


async def _inject_context(session: AsyncSession, messages: List[ChatMessage]) -> Optional[Dict[str, str]]:
    last_user = next((m.content for m in reversed(messages) if m.role == "user"), None)
    if not last_user:
        return None
    context = await gather_context_chunks(session, last_user)
    if not context:
        return None
    return {"role": "system", "content": f"السياق الداعم:\n{context}"}


@router.post("/chat")
async def chat_endpoint(
    chat_request: ChatRequest,
    accept: str = Header(default=""),
    user: User = Depends(ensure_rate_limit),
    session: AsyncSession = Depends(get_session),
) -> Response:
    start = time.perf_counter()

    tool_chunks: List[ChatStreamChunk] = []
    enriched_messages = list(chat_request.messages)

    # Execute pending tool calls provided by the assistant
    for message in chat_request.messages:
        if message.role == "assistant" and message.tool_calls:
            for call in message.tool_calls:
                tool = registry.get(call.name)
                result = tool.handler(call.arguments, user)
                chunk = ChatStreamChunk(
                    type="tool_result",
                    tool_name=call.name,
                    tool_arguments=call.arguments,
                    tool_result=result,
                    message_id=call.id or str(uuid.uuid4()),
                )
                tool_chunks.append(chunk)
                enriched_messages.append(
                    ChatMessage(
                        role="tool",
                        name=call.name,
                        content=json.dumps(result, ensure_ascii=False),
                    )
                )
                await _log_interaction(
                    session,
                    user,
                    role="tool",
                    content=json.dumps(result, ensure_ascii=False),
                    tool_name=call.name,
                )

    openai_messages = _to_openai_messages(enriched_messages)
    context_message = await _inject_context(session, enriched_messages)
    if context_message:
        openai_messages.append(context_message)

    for message in chat_request.messages:
        if message.role == "user":
            await _log_interaction(session, user, role="user", content=message.content)

    # Streaming branch
    if "text/event-stream" in accept:
        async def event_stream() -> AsyncGenerator[bytes, None]:
            assistant_text = ""
            for chunk in tool_chunks:
                payload = chunk.json()
                yield f"data: {payload}\n\n".encode("utf-8")
            try:
                async for raw in llm_client.stream_chat(
                    messages=openai_messages,
                    language=chat_request.options.lang,
                    temperature=chat_request.options.temperature,
                    tools=registry.as_openai_schema(),
                ):
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        data = {"type": "message", "delta": raw}
                    if data.get("type") == "message" and data.get("delta"):
                        assistant_text += data["delta"]
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")
            except HTTPException as exc:
                error_chunk = ChatStreamChunk(type="error", delta=str(exc.detail))
                yield f"data: {error_chunk.json()}\n\n".encode("utf-8")
            finally:
                latency_ms = int((time.perf_counter() - start) * 1000)
                if assistant_text:
                    await _log_interaction(session, user, role="assistant", content=assistant_text, latency_ms=latency_ms)
                done_chunk = ChatStreamChunk(type="done")
                yield f"data: {done_chunk.json()}\n\n".encode("utf-8")

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    completion = await llm_client.complete(
        messages=openai_messages,
        language=chat_request.options.lang,
        temperature=chat_request.options.temperature,
    )
    message_payload = completion["choices"][0]["message"]
    assistant_message = ChatMessage(**message_payload)
    latency_ms = int((time.perf_counter() - start) * 1000)
    await _log_interaction(session, user, role="assistant", content=assistant_message.content, latency_ms=latency_ms)
    response = ChatResponse(message=assistant_message, latency_ms=latency_ms)
    return JSONResponse(content=response.dict())
