import asyncio
from datetime import date, timedelta
from typing import Dict

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from backend.app.core.config import settings
from backend.app.db import models
from backend.app.db.database import AsyncSessionLocal, engine
from backend.app.db.models import Base
from backend.app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


async def _seed_data() -> Dict[str, int]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    today = date.today()

    async with AsyncSessionLocal() as session:
        admin = models.User(name="مدير", role="admin", email="admin@example.com")
        supervisor_user = models.User(name="مشرف", role="supervisor", email="sup@example.com")
        supervisor = models.Supervisor(user=supervisor_user, department="الصيانة")
        resident_user = models.User(name="مقيم", role="resident", email="res@example.com", unit_no="4B")
        resident = models.Resident(user=resident_user, unit_no="4B", start_date=today)
        subscription = models.Subscription(
            resident=resident,
            type="electricity",
            plan="أساسي",
            cycle="monthly",
            unit_price=150.0,
            next_due=today,
            active=True,
        )
        invoice = models.Invoice(
            resident=resident,
            subscription=subscription,
            amount=150.0,
            status=models.InvoiceStatusEnum.due.value,
            due_date=today,
            reference="INV-SEED",
        )
        asset = models.Asset(
            name="مولد كهرباء",
            category="كهرباء",
            serial_no="ASSET-001",
            warranty_until=today + timedelta(days=5),
            status="active",
        )
        ticket = models.MaintenanceTicket(
            asset=asset,
            title="فحص المولد",
            description="فحص دوري",
            status="open",
            priority="high",
            due_date=today + timedelta(days=2),
        )
        session.add_all([admin, supervisor, resident, subscription, invoice, asset, ticket])
        await session.commit()
        return {
            "admin_id": admin.id,
            "admin_user_id": admin.id,
            "supervisor_id": supervisor.id,
            "supervisor_user_id": supervisor.user_id,
            "resident_id": resident.id,
            "resident_user_id": resident.user_id,
            "subscription_id": subscription.id,
            "invoice_id": invoice.id,
            "asset_id": asset.id,
            "ticket_id": ticket.id,
        }


@pytest.fixture(scope="function")
def seed_ids() -> Dict[str, int]:
    return asyncio.run(_seed_data())


@pytest.fixture()
def token_factory() -> callable:
    def _factory(user_id: int, role: str) -> str:
        return jwt.encode({"sub": str(user_id), "role": role}, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return _factory
