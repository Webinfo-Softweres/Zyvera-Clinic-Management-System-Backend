from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import date, datetime


class PatientCreate(BaseModel):
    patient_name: str = Field(..., min_length=1, max_length=255, examples=["John Doe"])
    address: Optional[str] = Field(None, max_length=500)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    mobile: Optional[str] = Field(None, max_length=20)
    reg_date: Optional[date] = None


class PatientUpdate(BaseModel):
    patient_name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[Literal["Male", "Female", "Other"]] = None
    mobile: Optional[str] = Field(None, max_length=20)


class PatientResponse(BaseModel):
    id: str
    centre_code: str
    hospital_no: str
    reg_date: Optional[date] = None
    patient_name: str
    address: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    mobile: Optional[str] = None
    is_deleted: bool
    deleted_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientListFilter(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    patient_name: Optional[str] = None
    mobile: Optional[str] = None
    hospital_no: Optional[str] = None
