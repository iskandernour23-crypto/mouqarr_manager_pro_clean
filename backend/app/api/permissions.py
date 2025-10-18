from __future__ import annotations

from fastapi import Depends, HTTPException, status

from backend.app.api.utils import resolve_user
from backend.app.db import models


def require_roles(*roles: str):
    async def dependency(user: models.User = Depends(resolve_user)) -> models.User:
        if roles and user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency
