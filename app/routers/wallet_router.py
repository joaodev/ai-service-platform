from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import require_current_user
from app.database.session import get_db
from app.schemas.transaction_schema import TransactionCreate, TransactionResponse
from app.schemas.wallet_schema import WalletCreate, WalletResponse
from app.services.wallet_service import (
    create_transaction,
    create_wallet,
    get_transaction_by_id,
    get_wallet_balance,
    get_wallet_by_id,
    list_transactions,
    list_wallets,
)

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.get("", response_model=list[WalletResponse])
def list_wallets_endpoint(db: Session = Depends(get_db)) -> list[WalletResponse]:
    return list_wallets(db)


@router.get("/{wallet_id}", response_model=WalletResponse)
def get_wallet_endpoint(wallet_id: int, db: Session = Depends(get_db)) -> WalletResponse:
    return get_wallet_by_id(db, wallet_id)


@router.post("", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
def create_wallet_endpoint(
    payload: WalletCreate,
    _: object = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> WalletResponse:
    return create_wallet(db, payload)


@router.get("/{wallet_id}/balance")
def get_wallet_balance_endpoint(wallet_id: int, db: Session = Depends(get_db)) -> dict[str, float]:
    get_wallet_by_id(db, wallet_id)
    return {"wallet_id": wallet_id, "balance": get_wallet_balance(db, wallet_id)}


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions_endpoint(db: Session = Depends(get_db)) -> list[TransactionResponse]:
    return list_transactions(db)


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction_endpoint(
    transaction_id: int, db: Session = Depends(get_db)
) -> TransactionResponse:
    return get_transaction_by_id(db, transaction_id)


@router.post(
    "/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
def create_transaction_endpoint(
    payload: TransactionCreate,
    _: object = Depends(require_current_user),
    db: Session = Depends(get_db),
) -> TransactionResponse:
    return create_transaction(db, payload)
