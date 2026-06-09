from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional
from datetime import datetime


class ClinicalPageCreate(BaseModel):
    hospital_no: str = Field(..., description="Patient hospital number")
    data: Dict[str, Any] = Field(..., description="Flexible JSON data for the clinical page")


class ClinicalPageUpdate(BaseModel):
    data: Dict[str, Any] = Field(..., description="Updated JSON data for the clinical page")


class ClinicalPageResponse(BaseModel):
    id: str
    centre_code: str
    hospital_no: str
    page_no: int
    page_data: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseAggregateResponse(BaseModel):
    """Complete patient case with all clinical pages."""
    patient: Dict[str, Any]
    page1: Optional[Dict[str, Any]] = None
    page2: Optional[Dict[str, Any]] = None
    page3: Optional[Dict[str, Any]] = None
    page4: Optional[Dict[str, Any]] = None
    page5: Optional[Dict[str, Any]] = None
    page6: Optional[Dict[str, Any]] = None
    page7: Optional[Dict[str, Any]] = None
