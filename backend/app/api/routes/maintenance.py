from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.api import permissions, schemas
from backend.app.db import models
from backend.app.db.database import get_session
from backend.app.services import notifier

router = APIRouter()


@router.get("/", response_model=List[schemas.MaintenanceOut])
async def list_tickets(
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> List[schemas.MaintenanceOut]:
    statement = select(models.MaintenanceTicket)
    result = await session.execute(statement)
    tickets = result.scalars().all()
    return [schemas.MaintenanceOut.from_orm(ticket) for ticket in tickets]


@router.post("/", response_model=schemas.MaintenanceOut, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: schemas.MaintenanceCreate,
    session: AsyncSession = Depends(get_session),
    actor: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.MaintenanceOut:
    ticket = models.MaintenanceTicket(
        asset_id=payload.asset_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        status="open",
    )
    session.add(ticket)
    await session.flush()

    if actor.role == "supervisor":
        await notifier.create_notification(
            session,
            user_id=actor.id,
            title="تم إنشاء تذكرة جديدة",
            body=f"{ticket.title}",
        )

    return schemas.MaintenanceOut.from_orm(ticket)


@router.put("/{ticket_id}", response_model=schemas.MaintenanceOut)
async def update_ticket(
    ticket_id: int,
    payload: schemas.MaintenanceUpdate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.MaintenanceOut:
    statement = select(models.MaintenanceTicket).where(models.MaintenanceTicket.id == ticket_id)
    result = await session.execute(statement)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if payload.asset_id is not None:
        ticket.asset_id = payload.asset_id
    if payload.title is not None:
        ticket.title = payload.title
    if payload.description is not None:
        ticket.description = payload.description
    if payload.status is not None:
        ticket.status = payload.status
    if payload.priority is not None:
        ticket.priority = payload.priority
    if payload.assigned_to is not None:
        ticket.assigned_to = payload.assigned_to
    if payload.due_date is not None:
        ticket.due_date = payload.due_date
    if payload.closed_at is not None:
        ticket.closed_at = payload.closed_at

    await session.flush()
    return schemas.MaintenanceOut.from_orm(ticket)


@router.post("/{ticket_id}/assign/{supervisor_id}", response_model=schemas.MaintenanceOut)
async def assign_ticket(
    ticket_id: int,
    supervisor_id: int,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.MaintenanceOut:
    ticket_stmt = select(models.MaintenanceTicket).where(models.MaintenanceTicket.id == ticket_id)
    sup_stmt = select(models.Supervisor).options(selectinload(models.Supervisor.user)).where(models.Supervisor.id == supervisor_id)
    ticket_result = await session.execute(ticket_stmt)
    supervisor_result = await session.execute(sup_stmt)

    ticket = ticket_result.scalar_one_or_none()
    supervisor = supervisor_result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if not supervisor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supervisor not found")

    ticket.assigned_to = supervisor.id

    if supervisor.user:
        await notifier.create_notification(
            session,
            user_id=supervisor.user.id,
            title="تم تكليفك بتذكرة صيانة",
            body=ticket.title,
        )

    await session.flush()
    return schemas.MaintenanceOut.from_orm(ticket)
