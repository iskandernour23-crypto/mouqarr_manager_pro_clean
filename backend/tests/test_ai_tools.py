import asyncio

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.db.database import engine
from backend.app.db.models import Base

client = TestClient(app)


def _make_token(role: str) -> str:
    return jwt.encode({"sub": "user-test", "role": role}, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> None:
    async def _setup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_setup())
    yield
    async def _teardown() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    asyncio.run(_teardown())


def test_execute_action_admin() -> None:
    token = _make_token("admin")
    response = client.post(
        "/ai/actions/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "payments.summary", "params": {"period": "week"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "payments.summary"
    assert body["result"]["status"] == "ok"


def test_execute_action_forbidden() -> None:
    token = _make_token("resident")
    response = client.post(
        "/ai/actions/execute",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "payments.create_invoice", "params": {"resident_id": "1", "month": "2024-11"}},
    )
    assert response.status_code == 403
