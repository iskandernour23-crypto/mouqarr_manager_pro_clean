from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api import permissions, schemas
from backend.app.db import models
from backend.app.db.database import get_session

router = APIRouter()


@router.get("/", response_model=List[schemas.AssetOut])
async def list_assets(
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> List[schemas.AssetOut]:
    result = await session.execute(select(models.Asset))
    assets = result.scalars().all()
    return [schemas.AssetOut.from_orm(asset) for asset in assets]


@router.post("/", response_model=schemas.AssetOut, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: schemas.AssetCreate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.AssetOut:
    asset = models.Asset(
        name=payload.name,
        category=payload.category,
        serial_no=payload.serial_no,
        warranty_until=payload.warranty_until,
        status=payload.status,
    )
    session.add(asset)
    await session.flush()
    return schemas.AssetOut.from_orm(asset)


@router.put("/{asset_id}", response_model=schemas.AssetOut)
async def update_asset(
    asset_id: int,
    payload: schemas.AssetUpdate,
    session: AsyncSession = Depends(get_session),
    _: models.User = Depends(permissions.require_roles("admin", "supervisor")),
) -> schemas.AssetOut:
    result = await session.execute(select(models.Asset).where(models.Asset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    if payload.name is not None:
        asset.name = payload.name
    if payload.category is not None:
        asset.category = payload.category
    if payload.serial_no is not None:
        asset.serial_no = payload.serial_no
    if payload.warranty_until is not None:
        asset.warranty_until = payload.warranty_until
    if payload.status is not None:
        asset.status = payload.status

    await session.flush()
    return schemas.AssetOut.from_orm(asset)
