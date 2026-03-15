from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.transaction_schema import (
    AccountsPayableCreate,
    AccountsPayableResponse,
    AccountsReceivableCreate,
    AccountsReceivableResponse,
)
from app.services.finance_service import (
    create_accounts_payable,
    create_accounts_receivable,
    get_accounts_payable_by_id,
    get_accounts_receivable_by_id,
    list_accounts_payable,
    list_accounts_receivable,
)

router = APIRouter(prefix="/finance", tags=["Finance"])


@router.get("/accounts-payable", response_model=list[AccountsPayableResponse])
def list_accounts_payable_endpoint(db: Session = Depends(get_db)) -> list[AccountsPayableResponse]:
    return list_accounts_payable(db)


@router.get("/accounts-payable/{payable_id}", response_model=AccountsPayableResponse)
def get_accounts_payable_endpoint(
    payable_id: int, db: Session = Depends(get_db)
) -> AccountsPayableResponse:
    return get_accounts_payable_by_id(db, payable_id)


@router.post(
    "/accounts-payable",
    response_model=AccountsPayableResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_accounts_payable_endpoint(
    payload: AccountsPayableCreate,
    db: Session = Depends(get_db),
) -> AccountsPayableResponse:
    return create_accounts_payable(db, payload)


@router.get("/accounts-receivable", response_model=list[AccountsReceivableResponse])
def list_accounts_receivable_endpoint(
    db: Session = Depends(get_db),
) -> list[AccountsReceivableResponse]:
    return list_accounts_receivable(db)


@router.get("/accounts-receivable/{receivable_id}", response_model=AccountsReceivableResponse)
def get_accounts_receivable_endpoint(
    receivable_id: int, db: Session = Depends(get_db)
) -> AccountsReceivableResponse:
    return get_accounts_receivable_by_id(db, receivable_id)


@router.post(
    "/accounts-receivable",
    response_model=AccountsReceivableResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_accounts_receivable_endpoint(
    payload: AccountsReceivableCreate,
    db: Session = Depends(get_db),
) -> AccountsReceivableResponse:
    return create_accounts_receivable(db, payload)
