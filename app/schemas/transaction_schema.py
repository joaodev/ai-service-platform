from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.accounts_payable import AccountsPayableStatus
from app.models.accounts_receivable import AccountsReceivableStatus
from app.models.transaction import TransactionType


class TransactionCreate(BaseModel):
    wallet_id: int
    type: TransactionType
    amount: float
    description: str | None = None


class TransactionResponse(BaseModel):
    id: int
    wallet_id: int
    type: TransactionType
    amount: float
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountsPayableCreate(BaseModel):
    supplier_id: int
    description: str
    amount: float
    due_date: date
    status: AccountsPayableStatus = AccountsPayableStatus.PENDING


class AccountsPayableResponse(BaseModel):
    id: int
    supplier_id: int
    description: str
    amount: float
    due_date: date
    status: AccountsPayableStatus

    model_config = ConfigDict(from_attributes=True)


class AccountsReceivableCreate(BaseModel):
    customer_id: int
    description: str
    amount: float
    due_date: date
    status: AccountsReceivableStatus = AccountsReceivableStatus.PENDING


class AccountsReceivableResponse(BaseModel):
    id: int
    customer_id: int
    description: str
    amount: float
    due_date: date
    status: AccountsReceivableStatus

    model_config = ConfigDict(from_attributes=True)
