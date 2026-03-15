from sqlalchemy import Column, DateTime, JSON, String
from sqlalchemy.sql import func

from app.database.base import Base


class BackgroundTask(Base):
    __tablename__ = "background_tasks"

    id = Column(String, primary_key=True, index=True)
    task_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
