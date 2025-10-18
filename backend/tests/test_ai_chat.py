import asyncio

from fastapi.testclient import TestClient
from jose import jwt

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.database import engine
from backend.app.db.models import Base

client = TestClient(app)


def _ensure_tables() -> None:
    async def _setup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_setup())


def _make_token(role: str = "admin") -> str:
    return jwt.encode({"sub": "chat-user", "role": role}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def test_chat_returns_mock_response() -> None:
    _ensure_tables()
    token = _make_token()
    response = client.post(
        "/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "messages": [
                {"role": "user", "content": "ما هي أحدث الدفعات؟"},
            ],
            "options": {"lang": "ar"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"]["role"] == "assistant"
    assert "تمت معالجة" in body["message"]["content"]
