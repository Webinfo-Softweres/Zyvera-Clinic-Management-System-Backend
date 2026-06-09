from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import date


# ── Daily Report ──────────────────────────────────────────────────────────────

class DailyReportRequest(BaseModel):
    report_date: date = Field(..., description="Date for the daily report (YYYY-MM-DD)")


class DailyReportResponse(BaseModel):
    report_date: date
    total_registrations: int
    new_patients: int
    centre_code: str


# ── Monthly Report ────────────────────────────────────────────────────────────

class MonthlyReportRequest(BaseModel):
    month: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    year: int = Field(..., ge=2000, le=2100, description="Four-digit year")


class DailyBreakdown(BaseModel):
    report_date: date
    registrations: int


class MonthlyReportResponse(BaseModel):
    month: int
    year: int
    centre_code: str
    monthly_total: int
    daily_breakdown: List[DailyBreakdown]


# ── Patient History Report ────────────────────────────────────────────────────

class PatientHistoryReportResponse(BaseModel):
    patient: Dict[str, Any]
    clinical_pages: List[Dict[str, Any]]
    timeline: List[Dict[str, Any]]


# ── Doctor Summary Report ─────────────────────────────────────────────────────

class DoctorSummaryRequest(BaseModel):
    from_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    to_date: date = Field(..., description="End date (YYYY-MM-DD)")


class DoctorSummaryResponse(BaseModel):
    centre_code: str
    from_date: date
    to_date: date
    patients_seen: int
    cases_created: int
    clinical_records_entered: int


# ── PDF Export ────────────────────────────────────────────────────────────────

class PDFExportRequest(BaseModel):
    report_type: str = Field(
        ...,
        description="One of: daily | monthly | patient-history | doctor-summary"
    )
    params: Optional[Dict[str, Any]] = Field(
        None,
        description="Report-specific filter parameters"
    )
