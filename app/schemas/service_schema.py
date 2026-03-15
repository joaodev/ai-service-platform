from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    name: str
    description: str | None = None
    base_price: float


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str | None
    base_price: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
