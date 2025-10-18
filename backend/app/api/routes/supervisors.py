from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.api import permissions, schemas
from backend.app.api.utils import to_user_out
from backend.app.db import models
from backend.app.db.database import get_session

router = APIRouter()


@router.get("/", response_model=List[schemas.SupervisorOut])
async def list_supervisors(
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin")),
) -> List[schemas.SupervisorOut]:
    statement = select(models.Supervisor).options(selectinload(models.Supervisor.user))
    result = await session.execute(statement)
    supervisors = result.scalars().all()
    return [
        schemas.SupervisorOut(
            id=supervisor.id,
            department=supervisor.department,
            user=schemas.UserOut(**to_user_out(supervisor.user)),
        )
        for supervisor in supervisors
    ]


@router.post("/", response_model=schemas.SupervisorOut, status_code=status.HTTP_201_CREATED)
async def create_supervisor(
    payload: schemas.SupervisorCreate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin")),
) -> schemas.SupervisorOut:
    user = models.User(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        role="supervisor",
    )
    supervisor = models.Supervisor(user=user, department=payload.department)
    session.add(supervisor)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supervisor already exists") from exc

    return schemas.SupervisorOut(
        id=supervisor.id,
        department=supervisor.department,
        user=schemas.UserOut(**to_user_out(user)),
    )


@router.put("/{supervisor_id}", response_model=schemas.SupervisorOut)
async def update_supervisor(
    supervisor_id: int,
    payload: schemas.SupervisorUpdate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin")),
) -> schemas.SupervisorOut:
    statement = select(models.Supervisor).options(selectinload(models.Supervisor.user)).where(models.Supervisor.id == supervisor_id)
    result = await session.execute(statement)
    supervisor = result.scalar_one_or_none()
    if not supervisor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supervisor not found")

    if payload.department is not None:
        supervisor.department = payload.department
    if payload.phone is not None:
        supervisor.user.phone = payload.phone
    if payload.email is not None:
        supervisor.user.email = payload.email
    if payload.name is not None:
        supervisor.user.name = payload.name

    await session.flush()

    return schemas.SupervisorOut(
        id=supervisor.id,
        department=supervisor.department,
        user=schemas.UserOut(**to_user_out(supervisor.user)),
    )
