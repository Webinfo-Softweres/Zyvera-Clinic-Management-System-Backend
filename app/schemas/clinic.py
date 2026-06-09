from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date, datetime

class ClinicBase(BaseModel):
    clinic_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    license_expiry: Optional[date] = None

class ClinicCreate(ClinicBase):
    pass

class ClinicUpdate(BaseModel):
    clinic_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    license_expiry: Optional[date] = None

class ClinicStatusUpdate(BaseModel):
    status: str

class ClinicResponse(ClinicBase):
    id: str
    centre_code: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
