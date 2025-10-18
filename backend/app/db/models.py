from __future__ import annotations

import json
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=True)
    email = Column(String(255), nullable=True, unique=True)
    role = Column(String(32), nullable=False, index=True)
    unit_no = Column(String(32), nullable=True)

    resident = relationship("Resident", back_populates="user", uselist=False)
    supervisor = relationship("Supervisor", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Resident(Base, TimestampMixin):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    unit_no = Column(String(32), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    user = relationship("User", back_populates="resident")
    subscriptions = relationship("Subscription", back_populates="resident", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="resident", cascade="all, delete-orphan")


class Supervisor(Base, TimestampMixin):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    department = Column(String(128), nullable=True)

    user = relationship("User", back_populates="supervisor")
    tickets = relationship(
        "MaintenanceTicket",
        back_populates="assignee",
        cascade="all, delete-orphan",
        foreign_keys="MaintenanceTicket.assigned_to",
    )


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("resident_id", "type", name="uq_resident_subscription_type"),
    )

    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(64), nullable=False, index=True)
    plan = Column(String(128), nullable=True)
    cycle = Column(String(32), nullable=False, default="monthly")
    unit_price = Column(Numeric(10, 2), nullable=False)
    next_due = Column(Date, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    resident = relationship("Resident", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")


class InvoiceStatusEnum(str, Enum):
    draft = "draft"
    due = "due"
    paid = "paid"
    overdue = "overdue"
    cancelled = "cancelled"


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(32), nullable=False, default=InvoiceStatusEnum.due.value, index=True)
    due_date = Column(Date, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    reference = Column(String(64), nullable=False, unique=True)

    resident = relationship("Resident", back_populates="invoices")
    subscription = relationship("Subscription", back_populates="invoices")
    payments = relationship("PaymentLog", back_populates="invoice", cascade="all, delete-orphan")


class PaymentLog(Base, TimestampMixin):
    __tablename__ = "payment_logs"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False)

    invoice = relationship("Invoice", back_populates="payments")


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(128), nullable=False)
    serial_no = Column(String(128), nullable=False, unique=True)
    warranty_until = Column(Date, nullable=True)
    status = Column(String(32), nullable=False, default="active", index=True)

    tickets = relationship("MaintenanceTicket", back_populates="asset", cascade="all, delete-orphan")


class MaintenanceTicket(Base, TimestampMixin):
    __tablename__ = "maintenance_tickets"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="open", index=True)
    priority = Column(String(32), nullable=False, default="medium")
    assigned_to = Column(Integer, ForeignKey("supervisors.id", ondelete="SET NULL"), nullable=True)
    due_date = Column(Date, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    asset = relationship("Asset", back_populates="tickets")
    assignee = relationship("Supervisor", back_populates="tickets")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    channel = Column(String(32), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="notifications")


class EntityEmbedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    vector = Column(LargeBinary, nullable=False)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def vector_to_list(self) -> Optional[list[float]]:
        try:
            return json.loads(self.vector.decode("utf-8"))
        except Exception:
            return None

    @staticmethod
    def from_values(
        entity_type: str,
        entity_id: int,
        vector: list[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "EntityEmbedding":
        payload = json.dumps(vector).encode("utf-8")
        meta_str = json.dumps(metadata or {})
        return EntityEmbedding(
            entity_type=entity_type,
            entity_id=entity_id,
            vector=payload,
            metadata=meta_str,
        )


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    tool_name = Column(String(64), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role": self.role,
            "content": self.content,
            "tool_name": self.tool_name,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at.isoformat(),
        }


class AIEmbedding(Base):
    __tablename__ = "ai_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(128), nullable=False, index=True)
    chunk = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=False)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def embedding_to_list(self) -> Optional[list[float]]:
        try:
            return json.loads(self.embedding.decode("utf-8"))
        except Exception:
            return None

    @staticmethod
    def from_values(
        doc_id: str,
        chunk: str,
        vector: list[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AIEmbedding":
        payload = json.dumps(vector).encode("utf-8")
        meta_str = json.dumps(metadata or {})
        record = AIEmbedding(
            doc_id=doc_id,
            chunk=chunk,
            embedding=payload,
            metadata=meta_str,
        )
        return record
