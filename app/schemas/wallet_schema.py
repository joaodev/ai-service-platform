from datetime import datetime

from pydantic import BaseModel


class WalletCreate(BaseModel):
    user_id: int


class WalletResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
