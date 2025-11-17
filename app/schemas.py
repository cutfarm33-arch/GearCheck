from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import ItemStatus, JobStatus, TransactionType, UserRole


class UserBase(BaseModel):
    name: str
    email: str
    role: UserRole = UserRole.crew
    phone: Optional[str] = None
    notes: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    name: str
    client_name: Optional[str] = None
    shoot_start_date: Optional[date] = None
    shoot_end_date: Optional[date] = None
    location: Optional[str] = None
    producer_id: Optional[int] = None
    status: JobStatus = JobStatus.planned


class JobCreate(JobBase):
    pass


class JobRead(JobBase):
    id: int

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    name: str
    serial_number: Optional[str] = None
    category: Optional[str] = None
    status: ItemStatus = ItemStatus.available
    default_condition: Optional[str] = None
    notes: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    serial_number: Optional[str] = None
    category: Optional[str] = None
    status: Optional[ItemStatus] = None
    default_condition: Optional[str] = None
    notes: Optional[str] = None
    current_assignment_user_id: Optional[int] = Field(default=None)


class ItemRead(ItemBase):
    id: int
    current_assignment_user_id: Optional[int] = None

    class Config:
        from_attributes = True


class TransactionItemBase(BaseModel):
    item_id: int
    condition_notes: Optional[str] = None
    is_missing: bool = False
    is_damaged: bool = False
    photos: Optional[str] = None


class TransactionItemCheckout(TransactionItemBase):
    status_before: Optional[str] = None


class TransactionItemCheckin(TransactionItemBase):
    status_before: Optional[str] = None
    status_after: Optional[ItemStatus] = None


class TransactionBase(BaseModel):
    job_id: Optional[int] = None
    user_id: int
    assigned_to_user_id: Optional[int] = None
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    type: TransactionType
    items: List[TransactionItemCheckout | TransactionItemCheckin]


class TransactionItemRead(TransactionItemBase):
    id: int
    transaction_id: int
    status_before: Optional[str] = None
    status_after: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionRead(TransactionBase):
    id: int
    type: TransactionType
    timestamp: datetime
    items: List[TransactionItemRead]

    class Config:
        from_attributes = True
