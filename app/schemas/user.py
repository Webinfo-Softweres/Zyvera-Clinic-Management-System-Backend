from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal
from datetime import datetime

class UserBase(BaseModel):
    name: str
    username: str

class UserCreate(UserBase):
    password: str
    role: Literal["SUPER_ADMIN", "CLINIC_ADMIN", "CLINIC_USER"]
    centre_code: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[Literal["SUPER_ADMIN", "CLINIC_ADMIN", "CLINIC_USER"]] = None

class UserStatusUpdate(BaseModel):
    status: Literal["ACTIVE", "INACTIVE", "LOCKED"]

class UserResponse(UserBase):
    id: str
    centre_code: Optional[str] = None
    role: str
    status: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
