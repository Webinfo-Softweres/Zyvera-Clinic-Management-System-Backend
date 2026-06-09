import uuid
from sqlalchemy import (
    Column, String, Integer, DateTime, Boolean,
    Index, UniqueConstraint, Date
)
from app.core.database import Base
from datetime import datetime, timezone


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    centre_code = Column(String(20), index=True, nullable=False)
    hospital_no = Column(String(50), index=True, nullable=False)
    reg_date = Column(Date, index=True, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    patient_name = Column(String(255), nullable=False, index=True)
    address = Column(String(500), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    mobile = Column(String(20), nullable=True, index=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("centre_code", "hospital_no", name="uq_centre_hospital"),
        Index("ix_centre_hospital", "centre_code", "hospital_no"),
    )
