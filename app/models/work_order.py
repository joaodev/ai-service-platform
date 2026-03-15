import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.base import Base


class WorkOrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(WorkOrderStatus), nullable=False, default=WorkOrderStatus.CREATED)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    ticket = relationship("Ticket", back_populates="work_orders")
    assigned_user = relationship("User")
