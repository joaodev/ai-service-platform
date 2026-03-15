from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentActionItem(BaseModel):
    id: int
    agent_name: str
    event_type: str
    decision: str
    actions: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
