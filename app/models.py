from __future__ import annotations

import enum
from datetime import date, datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class UserRole(str, enum.Enum):
    admin = "admin"
    producer = "producer"
    crew = "crew"


class JobStatus(str, enum.Enum):
    planned = "planned"
    active = "active"
    completed = "completed"
    archived = "archived"


class ItemStatus(str, enum.Enum):
    available = "available"
    checked_out = "checked_out"
    in_repair = "in_repair"
    retired = "retired"
    missing = "missing"


class TransactionType(str, enum.Enum):
    check_out = "check_out"
    check_in = "check_in"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    role: UserRole = Field(default=UserRole.crew)
    phone: Optional[str] = None
    notes: Optional[str] = None

    produced_jobs: List["Job"] = Relationship(back_populates="producer")
    assigned_items: List["Item"] = Relationship(back_populates="current_assignee")
    transactions: List["Transaction"] = Relationship(back_populates="user")


class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    client_name: Optional[str] = None
    shoot_start_date: Optional[date] = None
    shoot_end_date: Optional[date] = None
    location: Optional[str] = None
    producer_id: Optional[int] = Field(default=None, foreign_key="users.id")
    status: JobStatus = Field(default=JobStatus.planned)

    producer: Optional[User] = Relationship(back_populates="produced_jobs")
    transactions: List["Transaction"] = Relationship(back_populates="job")


class Item(SQLModel, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    serial_number: Optional[str] = Field(default=None, unique=True, index=True)
    category: Optional[str] = None
    status: ItemStatus = Field(default=ItemStatus.available, index=True)
    default_condition: Optional[str] = None
    notes: Optional[str] = None
    current_assignment_user_id: Optional[int] = Field(default=None, foreign_key="users.id")

    current_assignee: Optional[User] = Relationship(back_populates="assigned_items")
    transaction_items: List["TransactionItem"] = Relationship(back_populates="item")


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    type: TransactionType = Field(index=True)
    job_id: Optional[int] = Field(default=None, foreign_key="jobs.id")
    user_id: int = Field(foreign_key="users.id")
    assigned_to_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    notes: Optional[str] = None

    user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Transaction.user_id"},
        back_populates="transactions",
    )
    job: Optional["Job"] = Relationship(back_populates="transactions")
    assigned_to_user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Transaction.assigned_to_user_id"}
    )
    items: List["TransactionItem"] = Relationship(back_populates="transaction")


class TransactionItem(SQLModel, table=True):
    __tablename__ = "transaction_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.id")
    item_id: int = Field(foreign_key="items.id")
    status_before: Optional[str] = None
    status_after: Optional[str] = None
    condition_notes: Optional[str] = None
    is_missing: bool = Field(default=False)
    is_damaged: bool = Field(default=False)
    photos: Optional[str] = None

    transaction: "Transaction" = Relationship(back_populates="items")
    item: "Item" = Relationship(back_populates="transaction_items")
