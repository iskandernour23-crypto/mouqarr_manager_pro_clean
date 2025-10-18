from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.api import permissions, schemas
from backend.app.db import models
from backend.app.db.database import get_session
from backend.app.services import notifier

router = APIRouter()


def _next_due(current: date, cycle: str) -> date:
    if cycle == "weekly":
        return current + timedelta(days=7)
    if cycle == "quarterly":
        return current + timedelta(days=90)
    if cycle == "yearly":
        return current + timedelta(days=365)
    return current + timedelta(days=30)


def _reference() -> str:
    return f"INV-{uuid.uuid4().hex[:10].upper()}"


@router.get("/", response_model=List[schemas.InvoiceOut])
async def list_invoices(
    status_filter: Optional[str] = Query(default=None, alias="status"),
    resident_id: Optional[int] = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> List[schemas.InvoiceOut]:
    statement = select(models.Invoice)
    if status_filter:
        statement = statement.where(models.Invoice.status == status_filter)
    if resident_id is not None:
        statement = statement.where(models.Invoice.resident_id == resident_id)
    result = await session.execute(statement)
    invoices = result.scalars().all()
    return [schemas.InvoiceOut.from_orm(inv) for inv in invoices]


@router.post("/", response_model=schemas.InvoiceOut, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: schemas.InvoiceCreate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.InvoiceOut:
    invoice = models.Invoice(
        resident_id=payload.resident_id,
        subscription_id=payload.subscription_id,
        amount=payload.amount,
        status=payload.status,
        due_date=payload.due_date,
        reference=_reference(),
    )
    session.add(invoice)
    await session.flush()
    return schemas.InvoiceOut.from_orm(invoice)


@router.post("/generate", response_model=schemas.InvoiceGenerateResult)
async def generate_invoices(
    payload: schemas.InvoiceGenerateRequest,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin")),
) -> schemas.InvoiceGenerateResult:
    target = payload.target_date
    statement = select(models.Subscription).where(
        and_(models.Subscription.active.is_(True), models.Subscription.next_due <= target)
    )
    result = await session.execute(statement)
    subscriptions = result.scalars().all()

    created = 0
    for subscription in subscriptions:
        invoice = models.Invoice(
            resident_id=subscription.resident_id,
            subscription_id=subscription.id,
            amount=float(subscription.unit_price),
            status=models.InvoiceStatusEnum.due.value,
            due_date=subscription.next_due,
            reference=_reference(),
        )
        session.add(invoice)
        subscription.next_due = _next_due(subscription.next_due, subscription.cycle)
        created += 1

    await session.flush()
    return schemas.InvoiceGenerateResult(created=created)


@router.post("/{invoice_id}/pay-mock", response_model=schemas.InvoiceOut)
async def pay_mock(
    invoice_id: int,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.InvoiceOut:
    statement = (
        select(models.Invoice)
        .options(selectinload(models.Invoice.resident).selectinload(models.Resident.user))
        .where(models.Invoice.id == invoice_id)
    )
    result = await session.execute(statement)
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    invoice.status = models.InvoiceStatusEnum.paid.value
    invoice.paid_at = datetime.utcnow()

    payment = models.PaymentLog(
        invoice_id=invoice.id,
        amount=invoice.amount,
        method="mock_gateway",
        status="success",
    )
    session.add(payment)

    if invoice.resident and invoice.resident.user:
        title = "تم استلام الدفع"
        body = f"تم دفع الفاتورة {invoice.reference} بقيمة {invoice.amount} بنجاح."
        await notifier.create_notification(
            session,
            user_id=invoice.resident.user.id,
            title=title,
            body=body,
        )

    await session.flush()
    return schemas.InvoiceOut.from_orm(invoice)
