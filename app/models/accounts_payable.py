import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class AccountsPayableStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class AccountsPayable(Base):
    __tablename__ = "accounts_payable"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(
        Enum(AccountsPayableStatus), nullable=False, default=AccountsPayableStatus.PENDING
    )

    supplier = relationship("Supplier", back_populates="accounts_payable")
