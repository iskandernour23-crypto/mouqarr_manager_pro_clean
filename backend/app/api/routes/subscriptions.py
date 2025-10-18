from __future__ import annotations

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api import permissions, schemas
from backend.app.db import models
from backend.app.db.database import get_session

router = APIRouter()


@router.get("/", response_model=List[schemas.SubscriptionOut])
async def list_subscriptions(
    resident_id: Optional[int] = Query(default=None),
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> List[schemas.SubscriptionOut]:
    statement = select(models.Subscription)
    if resident_id is not None:
        statement = statement.where(models.Subscription.resident_id == resident_id)
    result = await session.execute(statement)
    items = result.scalars().all()
    return [schemas.SubscriptionOut.from_orm(item) for item in items]


@router.post("/", response_model=schemas.SubscriptionOut, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    payload: schemas.SubscriptionCreate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.SubscriptionOut:
    statement = select(models.Resident).where(models.Resident.id == payload.resident_id)
    result = await session.execute(statement)
    resident = result.scalar_one_or_none()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    subscription = models.Subscription(
        resident_id=payload.resident_id,
        type=payload.type,
        plan=payload.plan,
        cycle=payload.cycle,
        unit_price=payload.unit_price,
        next_due=payload.next_due,
        active=payload.active,
    )
    session.add(subscription)
    await session.flush()
    return schemas.SubscriptionOut.from_orm(subscription)


@router.put("/{subscription_id}", response_model=schemas.SubscriptionOut)
async def update_subscription(
    subscription_id: int,
    payload: schemas.SubscriptionUpdate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.SubscriptionOut:
    statement = select(models.Subscription).where(models.Subscription.id == subscription_id)
    result = await session.execute(statement)
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    if payload.plan is not None:
        subscription.plan = payload.plan
    if payload.cycle is not None:
        subscription.cycle = payload.cycle
    if payload.unit_price is not None:
        subscription.unit_price = payload.unit_price
    if payload.next_due is not None:
        subscription.next_due = payload.next_due
    if payload.active is not None:
        subscription.active = payload.active

    await session.flush()
    return schemas.SubscriptionOut.from_orm(subscription)
