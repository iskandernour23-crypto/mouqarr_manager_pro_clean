from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    email: Optional[EmailStr]
    role: str
    unit_no: Optional[str]

    class Config:
        orm_mode = True


class ResidentBase(BaseModel):
    unit_no: str
    start_date: date
    end_date: Optional[date] = None


class ResidentCreate(ResidentBase):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class ResidentUpdate(BaseModel):
    unit_no: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class ResidentOut(ResidentBase):
    id: int
    user: UserOut

    class Config:
        orm_mode = True


class SupervisorCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None


class SupervisorUpdate(BaseModel):
    department: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class SupervisorOut(BaseModel):
    id: int
    department: Optional[str]
    user: UserOut

    class Config:
        orm_mode = True


class SubscriptionCreate(BaseModel):
    resident_id: int
    type: str
    plan: Optional[str] = None
    cycle: str = Field(default="monthly")
    unit_price: float
    next_due: date
    active: bool = True


class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None
    cycle: Optional[str] = None
    unit_price: Optional[float] = None
    next_due: Optional[date] = None
    active: Optional[bool] = None


class SubscriptionOut(BaseModel):
    id: int
    resident_id: int
    type: str
    plan: Optional[str]
    cycle: str
    unit_price: float
    next_due: date
    active: bool

    class Config:
        orm_mode = True


class InvoiceCreate(BaseModel):
    resident_id: int
    subscription_id: Optional[int] = None
    amount: float
    due_date: date
    status: str = "due"


class InvoiceGenerateRequest(BaseModel):
    target_date: date = Field(default_factory=date.today)


class InvoiceGenerateResult(BaseModel):
    created: int


class InvoiceOut(BaseModel):
    id: int
    resident_id: int
    subscription_id: Optional[int]
    amount: float
    status: str
    due_date: date
    paid_at: Optional[datetime]
    reference: str

    class Config:
        orm_mode = True


class PaymentLogOut(BaseModel):
    id: int
    invoice_id: int
    amount: float
    method: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class AssetCreate(BaseModel):
    name: str
    category: str
    serial_no: str
    warranty_until: Optional[date] = None
    status: str = "active"


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    serial_no: Optional[str] = None
    warranty_until: Optional[date] = None
    status: Optional[str] = None


class AssetOut(BaseModel):
    id: int
    name: str
    category: str
    serial_no: str
    warranty_until: Optional[date]
    status: str

    class Config:
        orm_mode = True


class MaintenanceCreate(BaseModel):
    asset_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[date] = None


class MaintenanceUpdate(BaseModel):
    asset_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[date] = None
    closed_at: Optional[datetime] = None


class MaintenanceOut(BaseModel):
    id: int
    asset_id: Optional[int]
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[int]
    due_date: Optional[date]
    closed_at: Optional[datetime]

    class Config:
        orm_mode = True


class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    channel: str
    sent_at: datetime
    read: bool

    class Config:
        orm_mode = True


class ReminderRunResult(BaseModel):
    overdue_invoices: int
    expiring_warranties: List[int]
    expiring_subscriptions: List[int]
    maintenance_due: List[int]


class LoginRequest(BaseModel):
    identifier: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
