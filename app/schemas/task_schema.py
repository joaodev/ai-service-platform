from datetime import datetime
from pydantic import BaseModel


class TaskStatusResponse(BaseModel):
    id: str
    task_type: str
    status: str
    payload: dict
    result: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True
