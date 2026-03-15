from sqlalchemy import func
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.events.event_publisher import publish_event
from app.events.event_types import EventType
from app.models.transaction import FinancialTransaction
from app.models.transaction import TransactionType
from app.models.wallet import Wallet
from app.schemas.transaction_schema import TransactionCreate
from app.schemas.wallet_schema import WalletCreate


def list_wallets(db: Session) -> list[Wallet]:
    return db.query(Wallet).all()


def get_wallet_by_id(db: Session, wallet_id: int) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return wallet


def create_wallet(db: Session, payload: WalletCreate) -> Wallet:
    wallet = Wallet(user_id=payload.user_id)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def list_transactions(db: Session) -> list[FinancialTransaction]:
    return db.query(FinancialTransaction).all()


def get_transaction_by_id(db: Session, transaction_id: int) -> FinancialTransaction:
    transaction = (
        db.query(FinancialTransaction).filter(FinancialTransaction.id == transaction_id).first()
    )
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


def create_transaction(db: Session, payload: TransactionCreate) -> FinancialTransaction:
    transaction = FinancialTransaction(
        wallet_id=payload.wallet_id,
        type=payload.type,
        amount=payload.amount,
        description=payload.description,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    payload_data = {
        "id": transaction.id,
        "wallet_id": transaction.wallet_id,
        "type": transaction.type.value,
        "amount": float(transaction.amount),
        "description": transaction.description,
    }

    publish_event(event_type=EventType.TRANSACTION_CREATED, payload=payload_data, db=db)

    if transaction.type == TransactionType.PAYMENT:
        publish_event(event_type=EventType.PAYMENT_RECEIVED, payload=payload_data, db=db)

    return transaction


def get_wallet_balance(db: Session, wallet_id: int) -> float:
    amount = (
        db.query(func.coalesce(func.sum(FinancialTransaction.amount), 0))
        .filter(FinancialTransaction.wallet_id == wallet_id)
        .scalar()
    )
    return float(amount)
