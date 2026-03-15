from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.accounts_payable import AccountsPayable
from app.models.accounts_receivable import AccountsReceivable
from app.schemas.transaction_schema import (
    AccountsPayableCreate,
    AccountsReceivableCreate,
)


def list_accounts_payable(db: Session) -> list[AccountsPayable]:
    return db.query(AccountsPayable).all()


def get_accounts_payable_by_id(db: Session, payable_id: int) -> AccountsPayable:
    payable = db.query(AccountsPayable).filter(AccountsPayable.id == payable_id).first()
    if not payable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Accounts payable not found"
        )
    return payable


def create_accounts_payable(db: Session, payload: AccountsPayableCreate) -> AccountsPayable:
    payable = AccountsPayable(
        supplier_id=payload.supplier_id,
        description=payload.description,
        amount=payload.amount,
        due_date=payload.due_date,
        status=payload.status,
    )
    db.add(payable)
    db.commit()
    db.refresh(payable)
    return payable


def list_accounts_receivable(db: Session) -> list[AccountsReceivable]:
    return db.query(AccountsReceivable).all()


def get_accounts_receivable_by_id(db: Session, receivable_id: int) -> AccountsReceivable:
    receivable = db.query(AccountsReceivable).filter(AccountsReceivable.id == receivable_id).first()
    if not receivable:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Accounts receivable not found"
        )
    return receivable


def create_accounts_receivable(
    db: Session, payload: AccountsReceivableCreate
) -> AccountsReceivable:
    receivable = AccountsReceivable(
        customer_id=payload.customer_id,
        description=payload.description,
        amount=payload.amount,
        due_date=payload.due_date,
        status=payload.status,
    )
    db.add(receivable)
    db.commit()
    db.refresh(receivable)
    return receivable
