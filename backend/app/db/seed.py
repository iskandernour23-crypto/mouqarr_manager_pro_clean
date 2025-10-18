from __future__ import annotations

import asyncio
from datetime import date, timedelta

from backend.app.db import models
from backend.app.db.database import AsyncSessionLocal


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        admin = models.User(name="مدير عام", role="admin", email="admin@mouqarr.local")
        supervisor_user = models.User(name="ليلى المشرفة", role="supervisor", email="supervisor@mouqarr.local")
        supervisor = models.Supervisor(user=supervisor_user, department="الصيانة")
        resident_user = models.User(name="حسين المقيم", role="resident", email="resident@mouqarr.local", unit_no="4B")
        resident = models.Resident(user=resident_user, unit_no="4B", start_date=date.today())

        electricity = models.Subscription(
            resident=resident,
            type="electricity",
            plan="أساسي",
            cycle="monthly",
            unit_price=175.0,
            next_due=date.today(),
        )
        water = models.Subscription(
            resident=resident,
            type="water",
            plan="عائلي",
            cycle="monthly",
            unit_price=90.0,
            next_due=date.today() + timedelta(days=5),
        )

        invoice = models.Invoice(
            resident=resident,
            subscription=electricity,
            amount=175.0,
            status=models.InvoiceStatusEnum.due.value,
            due_date=date.today(),
            reference="INV-SEED-001",
        )

        asset = models.Asset(
            name="مولد كهربائي",
            category="كهرباء",
            serial_no="ASSET-SEED-001",
            warranty_until=date.today() + timedelta(days=30),
            status="active",
        )

        ticket = models.MaintenanceTicket(
            asset=asset,
            title="فحص المولد الرئيسي",
            description="فحص شامل للمولد الرئيسي في السطح",
            status="open",
            priority="high",
            due_date=date.today() + timedelta(days=3),
        )

        session.add_all([admin, supervisor, resident, electricity, water, invoice, asset, ticket])
        await session.commit()


def run() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    run()
