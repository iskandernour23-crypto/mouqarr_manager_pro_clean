from fastapi import APIRouter

from . import assets, auth, invoices, maintenance, notifications, ops, residents, subscriptions, supervisors

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(residents.router, prefix="/residents", tags=["residents"])
api_router.include_router(supervisors.router, prefix="/supervisors", tags=["supervisors"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ops.router, prefix="/ops", tags=["ops"])
