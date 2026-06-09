import uuid
from sqlalchemy import Column, String, Integer, DateTime, JSON, Index, UniqueConstraint
from app.core.database import Base
from datetime import datetime, timezone


class ClinicalPage(Base):
    __tablename__ = "clinical_pages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    centre_code = Column(String(20), index=True, nullable=False)
    hospital_no = Column(String(50), index=True, nullable=False)
    page_no = Column(Integer, nullable=False, index=True)
    page_data = Column(JSON, nullable=True)

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
        UniqueConstraint("centre_code", "hospital_no", "page_no", name="uq_centre_hospital_page"),
        Index("ix_centre_hospital_page", "centre_code", "hospital_no"),
    )
