from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Awaitable, Callable, Dict, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from backend.app.api.deps import User
from backend.app.db import models
from backend.app.db.database import AsyncSessionLocal
from backend.app.services import notifier


Handler = Callable[[Dict[str, Any], User], Awaitable[Dict[str, Any]]]


@dataclass
class ToolDefinition:
    name: str
    description: str
    schema: Dict[str, Any]
    allowed_roles: Tuple[str, ...]
    handler: Handler


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        self._tools[definition.name] = definition

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found") from exc

    def as_openai_schema(self) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []
        for definition in self._tools.values():
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": definition.name,
                        "description": definition.description,
                        "parameters": definition.schema,
                    },
                }
            )
        return tools

    async def invoke(self, name: str, params: Dict[str, Any], user: User) -> Dict[str, Any]:
        tool = self.get(name)
        if tool.allowed_roles and user.role not in tool.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return await tool.handler(params, user)


registry = ToolRegistry()


async def _pay_invoice(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    invoice_id = int(params["invoice_id"])
    async with AsyncSessionLocal() as session:
        invoice = await session.get(
            models.Invoice,
            invoice_id,
            options=(selectinload(models.Invoice.resident).selectinload(models.Resident.user),),
        )
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        invoice.status = models.InvoiceStatusEnum.paid.value
        invoice.paid_at = datetime.utcnow()
        payment = models.PaymentLog(
            invoice_id=invoice.id,
            amount=invoice.amount,
            method=params.get("method", "assistant"),
            status="success",
        )
        session.add(payment)
        if invoice.resident and invoice.resident.user:
            await notifier.create_notification(
                session,
                user_id=invoice.resident.user.id,
                title="تم دفع الفاتورة",
                body=f"تم دفع الفاتورة {invoice.reference} من خلال المساعد.",
            )
        await session.commit()
        return {
            "status": "paid",
            "invoice_id": invoice.id,
            "reference": invoice.reference,
            "amount": float(invoice.amount),
        }


async def _create_ticket(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    async with AsyncSessionLocal() as session:
        ticket = models.MaintenanceTicket(
            asset_id=params.get("asset_id"),
            title=params["title"],
            description=params.get("description"),
            priority=params.get("priority", "medium"),
            due_date=params.get("due_date"),
            status="open",
        )
        session.add(ticket)
        await session.flush()
        supervisor_id = params.get("supervisor_id")
        if supervisor_id:
            supervisor = await session.get(
                models.Supervisor,
                int(supervisor_id),
                options=(selectinload(models.Supervisor.user),),
            )
            if supervisor and supervisor.user:
                ticket.assigned_to = supervisor.id
                await notifier.create_notification(
                    session,
                    user_id=supervisor.user.id,
                    title="تذكرة صيانة جديدة",
                    body=ticket.title,
                )
        await session.commit()
        return {
            "status": "created",
            "ticket_id": ticket.id,
            "title": ticket.title,
            "priority": ticket.priority,
        }


async def _notify_resident(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    resident_id = int(params["resident_id"])
    async with AsyncSessionLocal() as session:
        resident = await session.get(
            models.Resident,
            resident_id,
            options=(selectinload(models.Resident.user),),
        )
        if not resident or not resident.user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
        message = params.get("text", "")
        await notifier.create_notification(
            session,
            user_id=resident.user.id,
            title="رسالة من الإدارة",
            body=message,
        )
        await session.commit()
        return {"status": "sent", "resident_id": resident.id}


async def _summary_today(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    today = date.today()
    async with AsyncSessionLocal() as session:
        invoice_q = await session.execute(
            select(func.count()).select_from(models.Invoice).where(models.Invoice.due_date == today)
        )
        due_today = invoice_q.scalar_one()
        overdue_q = await session.execute(
            select(func.count()).select_from(models.Invoice).where(models.Invoice.status == models.InvoiceStatusEnum.overdue.value)
        )
        overdue_total = overdue_q.scalar_one()
        tickets_q = await session.execute(
            select(func.count()).select_from(models.MaintenanceTicket).where(models.MaintenanceTicket.status == "open")
        )
        open_tickets = tickets_q.scalar_one()
        return {
            "status": "ok",
            "invoices_due_today": due_today,
            "overdue_invoices": overdue_total,
            "open_tickets": open_tickets,
        }


def init_tools() -> None:
    registry.register(
        ToolDefinition(
            name="pay_invoice",
            description="دفع فاتورة محددة",
            schema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "integer"},
                    "method": {"type": "string"},
                },
                "required": ["invoice_id"],
            },
            allowed_roles=("admin", "supervisor"),
            handler=_pay_invoice,
        )
    )
    registry.register(
        ToolDefinition(
            name="create_ticket",
            description="إنشاء تذكرة صيانة",
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "asset_id": {"type": "integer"},
                    "priority": {"type": "string"},
                    "due_date": {"type": "string", "format": "date"},
                    "supervisor_id": {"type": "integer"},
                },
                "required": ["title"],
            },
            allowed_roles=("admin", "supervisor"),
            handler=_create_ticket,
        )
    )
    registry.register(
        ToolDefinition(
            name="notify_resident",
            description="إرسال إشعار للمقيم",
            schema={
                "type": "object",
                "properties": {
                    "resident_id": {"type": "integer"},
                    "text": {"type": "string"},
                },
                "required": ["resident_id", "text"],
            },
            allowed_roles=("admin", "supervisor"),
            handler=_notify_resident,
        )
    )
    registry.register(
        ToolDefinition(
            name="summary_today",
            description="ملخص اليوم للمشرفين",
            schema={"type": "object", "properties": {}},
            allowed_roles=("admin", "supervisor"),
            handler=_summary_today,
        )
    )


init_tools()
