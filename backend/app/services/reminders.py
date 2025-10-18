from __future__ import annotations

from datetime import date, timedelta
from typing import List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.api import schemas
from backend.app.db import models
from backend.app.services import notifier


async def run(session: AsyncSession) -> schemas.ReminderRunResult:
    today = date.today()
    soon = today + timedelta(days=7)

    overdue_invoices = 0
    invoice_stmt = (
        select(models.Invoice)
        .options(selectinload(models.Invoice.resident).selectinload(models.Resident.user))
        .where(
            and_(
                models.Invoice.status != models.InvoiceStatusEnum.paid.value,
                models.Invoice.due_date < today,
            )
        )
    )
    invoice_result = await session.execute(invoice_stmt)
    for invoice in invoice_result.scalars():
        if invoice.status != models.InvoiceStatusEnum.overdue.value:
            invoice.status = models.InvoiceStatusEnum.overdue.value
        overdue_invoices += 1
        if invoice.resident and invoice.resident.user:
            await notifier.create_notification(
                session,
                user_id=invoice.resident.user.id,
                title="فاتورة متأخرة",
                body=f"الرجاء سداد الفاتورة {invoice.reference} المستحقة بتاريخ {invoice.due_date}",
            )

    warranty_stmt = select(models.Asset).where(
        and_(models.Asset.warranty_until.is_not(None), models.Asset.warranty_until <= soon)
    )
    warranty_result = await session.execute(warranty_stmt)
    expiring_warranties: List[int] = []
    supervisors = await session.execute(select(models.Supervisor).options(selectinload(models.Supervisor.user)))
    supervisor_entities = [sup for sup in supervisors.scalars().all() if sup.user]
    for asset in warranty_result.scalars():
        expiring_warranties.append(asset.id)
        await notifier.notify_users(
            session,
            users=[sup.user for sup in supervisor_entities],
            title="ضمان أصل يوشك على الانتهاء",
            body=f"ضمان الأصل {asset.name} ينتهي في {asset.warranty_until}",
        )

    subscription_stmt = select(models.Subscription).where(
        and_(models.Subscription.active.is_(True), models.Subscription.next_due <= soon)
    )
    subscription_result = await session.execute(subscription_stmt)
    expiring_subscriptions: List[int] = []
    for subscription in subscription_result.scalars():
        expiring_subscriptions.append(subscription.id)
        resident_stmt = select(models.Resident).options(selectinload(models.Resident.user)).where(
            models.Resident.id == subscription.resident_id
        )
        resident_result = await session.execute(resident_stmt)
        resident = resident_result.scalar_one_or_none()
        if resident and resident.user:
            await notifier.create_notification(
                session,
                user_id=resident.user.id,
                title="تجديد الاشتراك",
                body=f"اشتراك {subscription.type} مستحق في {subscription.next_due}",
            )

    maintenance_stmt = select(models.MaintenanceTicket).where(
        and_(models.MaintenanceTicket.status == "open", models.MaintenanceTicket.due_date <= soon)
    )
    maintenance_result = await session.execute(maintenance_stmt)
    maintenance_due = [ticket.id for ticket in maintenance_result.scalars()]

    await session.flush()

    return schemas.ReminderRunResult(
        overdue_invoices=overdue_invoices,
        expiring_warranties=expiring_warranties,
        expiring_subscriptions=expiring_subscriptions,
        maintenance_due=maintenance_due,
    )
