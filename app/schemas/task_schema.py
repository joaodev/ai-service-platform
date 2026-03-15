from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TaskStatusResponse(BaseModel):
    id: str
    task_type: str
    status: str
    payload: dict
    result: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
