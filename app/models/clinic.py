import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.utils.constants import CLINIC_ACTIVE, CLINIC_SUSPENDED, CLINIC_INACTIVE
from datetime import datetime, timezone

class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    centre_code = Column(String(20), unique=True, index=True, nullable=False)
    clinic_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    status = Column(Enum(CLINIC_ACTIVE, CLINIC_SUSPENDED, CLINIC_INACTIVE, name="clinic_status"), default=CLINIC_ACTIVE, index=True, nullable=False)
    license_expiry = Column(Date, index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)

    users = relationship("User", back_populates="clinic", cascade="all, delete-orphan")
