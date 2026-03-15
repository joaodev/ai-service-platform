from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.sql import func

from app.database.base import Base


class AIAgentAction(Base):
    __tablename__ = "ai_agent_actions"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    decision = Column(String, nullable=False)
    actions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
