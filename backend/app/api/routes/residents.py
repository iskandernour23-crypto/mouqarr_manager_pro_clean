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


@router.get("/", response_model=List[schemas.ResidentOut])
async def list_residents(
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> List[schemas.ResidentOut]:
    statement = select(models.Resident).options(selectinload(models.Resident.user))
    result = await session.execute(statement)
    residents = result.scalars().all()
    return [
        schemas.ResidentOut(
            id=resident.id,
            unit_no=resident.unit_no,
            start_date=resident.start_date,
            end_date=resident.end_date,
            user=schemas.UserOut(**to_user_out(resident.user)),
        )
        for resident in residents
    ]


@router.post("/", response_model=schemas.ResidentOut, status_code=status.HTTP_201_CREATED)
async def create_resident(
    payload: schemas.ResidentCreate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin")),
) -> schemas.ResidentOut:
    user = models.User(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        role="resident",
        unit_no=payload.unit_no,
    )
    resident = models.Resident(
        user=user,
        unit_no=payload.unit_no,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    session.add(resident)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resident already exists") from exc

    return schemas.ResidentOut(
        id=resident.id,
        unit_no=resident.unit_no,
        start_date=resident.start_date,
        end_date=resident.end_date,
        user=schemas.UserOut(**to_user_out(user)),
    )


@router.put("/{resident_id}", response_model=schemas.ResidentOut)
async def update_resident(
    resident_id: int,
    payload: schemas.ResidentUpdate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.ResidentOut:
    statement = select(models.Resident).options(selectinload(models.Resident.user)).where(models.Resident.id == resident_id)
    result = await session.execute(statement)
    resident = result.scalar_one_or_none()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    if payload.unit_no is not None:
        resident.unit_no = payload.unit_no
        resident.user.unit_no = payload.unit_no
    if payload.start_date is not None:
        resident.start_date = payload.start_date
    if payload.end_date is not None:
        resident.end_date = payload.end_date
    if payload.phone is not None:
        resident.user.phone = payload.phone
    if payload.email is not None:
        resident.user.email = payload.email
    if payload.name is not None:
        resident.user.name = payload.name

    await session.flush()

    return schemas.ResidentOut(
        id=resident.id,
        unit_no=resident.unit_no,
        start_date=resident.start_date,
        end_date=resident.end_date,
        user=schemas.UserOut(**to_user_out(resident.user)),
    )


@router.post("/{resident_id}/assign-unit", response_model=schemas.ResidentOut)
async def assign_unit(
    resident_id: int,
    unit_no: str,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.ResidentOut:
    statement = select(models.Resident).options(selectinload(models.Resident.user)).where(models.Resident.id == resident_id)
    result = await session.execute(statement)
    resident = result.scalar_one_or_none()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    resident.unit_no = unit_no
    resident.user.unit_no = unit_no
    await session.flush()

    return schemas.ResidentOut(
        id=resident.id,
        unit_no=resident.unit_no,
        start_date=resident.start_date,
        end_date=resident.end_date,
        user=schemas.UserOut(**to_user_out(resident.user)),
    )
