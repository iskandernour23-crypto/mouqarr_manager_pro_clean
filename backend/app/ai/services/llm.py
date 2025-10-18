from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, Iterable, List, Optional

import httpx

from backend.app.core.config import settings

_SYSTEM_PROMPT_AR = """أنت مساعد إداري لمنصة سكنية تدعى "مقر برو". ساعد المشرفين على إدارة المقيمين، الفواتير، الدفعات، والصيانة. كن دقيقاً، موجزاً، وقدم اقتراحات عملية عند الحاجة."""
_SYSTEM_PROMPT_EN = "You are an operations assistant for the Mouqarr residential management platform. Help staff manage residents, billing, payments, and maintenance with concise, actionable answers."


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model

    def _system_prompt(self, language: str) -> str:
        return _SYSTEM_PROMPT_AR if language.startswith("ar") else _SYSTEM_PROMPT_EN

    async def _mock_stream(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        yield json.dumps({"type": "message", "delta": f"(mock) استلمت سؤالك: {last_user}"})
        await asyncio.sleep(0.01)
        yield json.dumps({"type": "done"})

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        language: str = "ar",
        temperature: float = 0.2,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            async for chunk in self._mock_stream(messages):
                yield chunk
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "system", "content": self._system_prompt(language)}] + messages,
            "temperature": temperature,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=60.0)) as client:
            async with client.stream("POST", "https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data = line[len("data: "):]
                    else:
                        data = line
                    if data.strip() == "[DONE]":
                        yield json.dumps({"type": "done"})
                        break
                    yield data

    async def complete(self, messages: List[Dict[str, Any]], language: str = "ar", temperature: float = 0.2) -> Dict[str, Any]:
        if not self.api_key:
            text = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "" )
            return {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": f"(mock) تمت معالجة الرسالة: {text}",
                        }
                    }
                ]
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "system", "content": self._system_prompt(language)}] + messages,
            "temperature": temperature,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=60.0)) as client:
            response = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            return response.json()


llm_client = LLMClient()
