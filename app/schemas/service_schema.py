from datetime import datetime

from pydantic import BaseModel


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

    class Config:
        from_attributes = True
