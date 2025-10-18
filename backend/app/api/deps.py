from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Deque, Dict, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.app.core.config import settings


security = HTTPBearer(auto_error=False)
_rate_limit_cache: Dict[str, Deque[float]] = defaultdict(deque)


class User:
    def __init__(self, user_id: str, role: str):
        self.id = user_id
        self.role = role


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user_id = payload.get("sub")
    role = payload.get("role", "resident")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return User(user_id=user_id, role=role)


async def ensure_rate_limit(user: User = Depends(get_current_user)) -> User:
    bucket = _rate_limit_cache[user.id]
    now = time.time()
    while bucket and now - bucket[0] > settings.rate_limit_period:
        bucket.popleft()

    if len(bucket) >= settings.rate_limit_per_user:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    bucket.append(now)
    return user
