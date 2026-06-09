import uuid
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.utils.constants import USER_ACTIVE, USER_INACTIVE, USER_LOCKED, SUPER_ADMIN, CLINIC_ADMIN, CLINIC_USER
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    centre_code = Column(String(20), ForeignKey("clinics.centre_code"), index=True, nullable=True)
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(SUPER_ADMIN, CLINIC_ADMIN, CLINIC_USER, name="user_role"), index=True, nullable=False)
    status = Column(Enum(USER_ACTIVE, USER_INACTIVE, USER_LOCKED, name="user_status"), default=USER_ACTIVE, index=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)

    clinic = relationship("Clinic", back_populates="users")
