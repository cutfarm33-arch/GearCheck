from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Item, ItemStatus, Transaction, TransactionItem, TransactionType
from ..schemas import TransactionCreate, TransactionRead

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _validate_items(item_ids: List[int], session: Session) -> List[Item]:
    items: List[Item] = []
    for item_id in item_ids:
        item = session.get(Item, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
        items.append(item)
    return items


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, session: Session = Depends(get_session)) -> Transaction:
    items = _validate_items([item.item_id for item in payload.items], session)
    transaction = Transaction(
        type=payload.type,
        job_id=payload.job_id,
        user_id=payload.user_id,
        assigned_to_user_id=payload.assigned_to_user_id,
        notes=payload.notes,
        timestamp=datetime.utcnow(),
    )
    session.add(transaction)
    session.flush()

    transaction_items: List[TransactionItem] = []
    for item_payload, item in zip(payload.items, items):
        previous_status = item.status.value
        if payload.type == TransactionType.check_out:
            if item.status not in {ItemStatus.available, ItemStatus.in_repair}:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item {item.id} is not available for checkout (status: {item.status})",
                )
            item.status = ItemStatus.checked_out
            item.current_assignment_user_id = payload.assigned_to_user_id or payload.user_id
            transaction_items.append(
                TransactionItem(
                    transaction_id=transaction.id,
                    item_id=item.id,
                    status_before=item_payload.status_before or previous_status,
                    condition_notes=item_payload.condition_notes,
                    is_missing=item_payload.is_missing,
                    is_damaged=item_payload.is_damaged,
                    photos=item_payload.photos,
                )
            )
        elif payload.type == TransactionType.check_in:
            status_after = item_payload.status_after or ItemStatus.available
            if item_payload.is_missing:
                item.status = ItemStatus.missing
            elif item_payload.is_damaged:
                item.status = ItemStatus.in_repair
            else:
                item.status = status_after
            if item.status == ItemStatus.available:
                item.current_assignment_user_id = None
            transaction_items.append(
                TransactionItem(
                    transaction_id=transaction.id,
                    item_id=item.id,
                    status_before=item_payload.status_before or previous_status,
                    status_after=status_after.value,
                    condition_notes=item_payload.condition_notes,
                    is_missing=item_payload.is_missing,
                    is_damaged=item_payload.is_damaged,
                    photos=item_payload.photos,
                )
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported transaction type")

    session.add_all(transaction_items)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.get("/", response_model=list[TransactionRead])
def list_transactions(session: Session = Depends(get_session)) -> list[Transaction]:
    transactions = session.exec(select(Transaction).order_by(Transaction.timestamp.desc())).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, session: Session = Depends(get_session)) -> Transaction:
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction
