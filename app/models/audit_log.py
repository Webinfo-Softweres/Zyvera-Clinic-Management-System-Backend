import uuid
from sqlalchemy import Column, String, DateTime
from app.core.database import Base
from datetime import datetime, timezone

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    centre_code = Column(String(20), index=True, nullable=False)
    user_id = Column(String(36), index=True, nullable=True)
    action = Column(String(100), index=True, nullable=False)
    module = Column(String(100), nullable=False)
    record_id = Column(String(100), nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
