from sqlalchemy import Column, DateTime, Integer, JSON, Text
from sqlalchemy.sql import func

from app.database.base import Base


class AIAgentLog(Base):
    __tablename__ = "ai_agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    input_message = Column(Text, nullable=False)
    actions_taken = Column(JSON, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
