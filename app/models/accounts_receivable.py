import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class AccountsReceivableStatus(str, enum.Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class AccountsReceivable(Base):
    __tablename__ = "accounts_receivable"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(
        Enum(AccountsReceivableStatus), nullable=False, default=AccountsReceivableStatus.PENDING
    )

    customer = relationship("Customer", back_populates="accounts_receivable")
