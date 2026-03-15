from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.work_order import WorkOrderStatus


class WorkOrderCreate(BaseModel):
    ticket_id: int
    assigned_user_id: int
    status: WorkOrderStatus = WorkOrderStatus.CREATED
    started_at: datetime | None = None
    finished_at: datetime | None = None


class WorkOrderResponse(BaseModel):
    id: int
    ticket_id: int
    assigned_user_id: int
    status: WorkOrderStatus
    started_at: datetime | None
    finished_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
