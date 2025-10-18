from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict

from fastapi import HTTPException, status

from backend.app.api.deps import User


@dataclass
class ToolDefinition:
    name: str
    description: str
    schema: Dict[str, Any]
    allowed_roles: tuple[str, ...]
    handler: Callable[[Dict[str, Any], User], Dict[str, Any]]


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


registry = ToolRegistry()


def _require_role(user: User, allowed_roles: tuple[str, ...]) -> None:
    if user.role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


# Tool handlers

def _residents_create(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    _require_role(user, ("admin", "supervisor"))
    return {
        "status": "created",
        "entity": "resident",
        "data": params,
        "message": "تم إنشاء المقيم بنجاح",
    }


def _residents_find(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    _require_role(user, ("admin", "supervisor", "resident"))
    query = params.get("query", "")
    return {
        "status": "ok",
        "entity": "resident",
        "data": [{"name": "أحمد علي", "unit": "12", "phone": "+966500000"}],
        "query": query,
    }


def _payments_create_invoice(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    _require_role(user, ("admin", "supervisor"))
    return {
        "status": "invoice_created",
        "entity": "invoice",
        "data": params,
    }


def _payments_overdue(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    _require_role(user, ("admin", "supervisor"))
    threshold = params.get("days_threshold", 30)
    return {
        "status": "ok",
        "overdue_residents": [
            {"resident": "خالد", "unit": "8", "days": threshold + 2},
        ],
    }


def _payments_summary(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    _require_role(user, ("admin", "supervisor"))
    period = params.get("period", "week")
    return {
        "status": "ok",
        "period": period,
        "total": 12500,
        "currency": "SAR",
    }


def _inventory_schedule_maintenance(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    _require_role(user, ("admin", "supervisor"))
    return {
        "status": "scheduled",
        "entity": "maintenance",
        "data": params,
    }


def _notifications_create(params: Dict[str, Any], user: User) -> Dict[str, Any]:
    _require_role(user, ("admin", "supervisor"))
    return {
        "status": "queued",
        "entity": "notification",
        "data": params,
    }


def init_tools() -> None:
    registry.register(
        ToolDefinition(
            name="residents.create",
            description="إنشاء مقيم جديد",
            schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string"},
                    "unit": {"type": "string"},
                    "start_date": {"type": "string", "format": "date"},
                },
                "required": ["name", "unit"],
            },
            allowed_roles=("admin", "supervisor"),
            handler=_residents_create,
        )
    )
    registry.register(
        ToolDefinition(
            name="residents.find",
            description="البحث عن مقيم",
            schema={
                "type": "object",
                "properties": {"query": {"type": "string"}},
            },
            allowed_roles=("admin", "supervisor", "resident"),
            handler=_residents_find,
        )
    )
    registry.register(
        ToolDefinition(
            name="payments.create_invoice",
            description="إنشاء فاتورة",
            schema={
                "type": "object",
                "properties": {
                    "resident_id": {"type": "string"},
                    "month": {"type": "string"},
                    "services": {
                        "type": "object",
                        "properties": {
                            "rent": {"type": "number"},
                            "water": {"type": "number"},
                            "electricity": {"type": "number"},
                            "maintenance": {"type": "number"},
                        },
                    },
                },
                "required": ["resident_id", "month"],
            },
            allowed_roles=("admin", "supervisor"),
            handler=_payments_create_invoice,
        )
    )
    registry.register(
        ToolDefinition(
            name="payments.overdue",
            description="قائمة المتأخرين",
            schema={
                "type": "object",
                "properties": {"days_threshold": {"type": "integer", "default": 30}},
            },
            allowed_roles=("admin", "supervisor"),
            handler=_payments_overdue,
        )
    )
    registry.register(
        ToolDefinition(
            name="payments.summary",
            description="ملخص المدفوعات",
            schema={
                "type": "object",
                "properties": {
                    "period": {"type": "string", "enum": ["day", "week", "month"]},
                },
            },
            allowed_roles=("admin", "supervisor"),
            handler=_payments_summary,
        )
    )
    registry.register(
        ToolDefinition(
            name="inventory.schedule_maintenance",
            description="جدولة صيانة عنصر",
            schema={
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                    "note": {"type": "string"},
                },
                "required": ["item_id", "date"],
            },
            allowed_roles=("admin", "supervisor"),
            handler=_inventory_schedule_maintenance,
        )
    )
    registry.register(
        ToolDefinition(
            name="notifications.create",
            description="إرسال إشعار",
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                    "audience": {"type": "string"},
                },
                "required": ["title", "body"],
            },
            allowed_roles=("admin", "supervisor"),
            handler=_notifications_create,
        )
    )


init_tools()
