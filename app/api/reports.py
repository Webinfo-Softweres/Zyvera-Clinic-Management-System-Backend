from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.schemas.report import (
    DailyReportResponse,
    MonthlyReportResponse,
    PatientHistoryReportResponse,
    DoctorSummaryResponse,
)
from app.schemas.common import SuccessResponse
from app.services.report_service import report_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.utils.pdf_generator import (
    generate_daily_pdf,
    generate_monthly_pdf,
    generate_patient_history_pdf,
    generate_doctor_summary_pdf,
)
from app.core.exceptions import BadRequestException

router = APIRouter(tags=["Reports"])


# ── Daily Report ──────────────────────────────────────────────────────────────

@router.get(
    "/daily",
    response_model=SuccessResponse[DailyReportResponse],
    summary="Daily registration report",
    description="Returns total registrations and new patients for a specific date.",
)
def daily_report(
    date: date = Query(..., description="Report date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = report_service.get_daily_report(db, centre_code=current_user.centre_code, report_date=date)
    return SuccessResponse(data=data)


# ── Monthly Report ────────────────────────────────────────────────────────────

@router.get(
    "/monthly",
    response_model=SuccessResponse[MonthlyReportResponse],
    summary="Monthly registration report",
    description="Returns daily breakdown and monthly total for the given month and year.",
)
def monthly_report(
    month: int = Query(..., ge=1, le=12, description="Month (1–12)"),
    year: int = Query(..., ge=2000, le=2100, description="Four-digit year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = report_service.get_monthly_report(db, centre_code=current_user.centre_code, month=month, year=year)
    return SuccessResponse(data=data)


# ── Patient History Report ────────────────────────────────────────────────────

@router.get(
    "/patient-history",
    response_model=SuccessResponse[PatientHistoryReportResponse],
    summary="Patient history report",
    description="Returns patient details, all clinical pages, and a timeline of changes.",
)
def patient_history_report(
    hospital_no: str = Query(..., description="Patient hospital number, e.g. HSP000001"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = report_service.get_patient_history(db, centre_code=current_user.centre_code, hospital_no=hospital_no)
    return SuccessResponse(data=data)


# ── Doctor Summary Report ─────────────────────────────────────────────────────

@router.get(
    "/doctor-summary",
    response_model=SuccessResponse[DoctorSummaryResponse],
    summary="Doctor summary report",
    description="Returns patients seen, cases created, and clinical records entered in a date range.",
)
def doctor_summary_report(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = report_service.get_doctor_summary(
        db, centre_code=current_user.centre_code, from_date=from_date, to_date=to_date
    )
    return SuccessResponse(data=data)


# ── PDF Export ────────────────────────────────────────────────────────────────

@router.get(
    "/export-pdf",
    summary="Export report as PDF",
    description=(
        "Generates and downloads a professional PDF report. "
        "report_type must be one of: daily | monthly | patient-history | doctor-summary. "
        "Pass additional filter parameters as query strings (date, month, year, hospital_no, from_date, to_date)."
    ),
    response_class=StreamingResponse,
    responses={200: {"content": {"application/pdf": {}}}},
)
def export_pdf(
    report_type: str = Query(..., description="daily | monthly | patient-history | doctor-summary"),
    # daily
    date: Optional[date] = Query(None, description="For daily report"),
    # monthly
    month: Optional[int] = Query(None, ge=1, le=12, description="For monthly report"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="For monthly report"),
    # patient-history
    hospital_no: Optional[str] = Query(None, description="For patient-history report"),
    # doctor-summary
    from_date: Optional[date] = Query(None, description="For doctor-summary report"),
    to_date: Optional[date] = Query(None, description="For doctor-summary report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from datetime import date as dt_date
    params = {}
    if date:
        params["date"] = str(date)
    if month:
        params["month"] = month
    if year:
        params["year"] = year
    if hospital_no:
        params["hospital_no"] = hospital_no
    if from_date:
        params["from_date"] = str(from_date)
    if to_date:
        params["to_date"] = str(to_date)

    report_data = report_service.get_report_data_for_pdf(
        db, centre_code=current_user.centre_code, report_type=report_type, params=params
    )

    clinic_name = getattr(current_user, "clinic", None)
    if clinic_name and hasattr(clinic_name, "clinic_name"):
        clinic_name = clinic_name.clinic_name
    else:
        clinic_name = current_user.centre_code

    if report_type == "daily":
        pdf_bytes = generate_daily_pdf(report_data, clinic_name=clinic_name)
        filename = f"daily_report_{params.get('date', 'report')}.pdf"
    elif report_type == "monthly":
        pdf_bytes = generate_monthly_pdf(report_data, clinic_name=clinic_name)
        filename = f"monthly_report_{params.get('year', '')}_{params.get('month', '')}.pdf"
    elif report_type == "patient-history":
        pdf_bytes = generate_patient_history_pdf(report_data, clinic_name=clinic_name)
        filename = f"patient_history_{hospital_no}.pdf"
    elif report_type == "doctor-summary":
        pdf_bytes = generate_doctor_summary_pdf(report_data, clinic_name=clinic_name)
        filename = f"doctor_summary_{params.get('from_date', '')}_{params.get('to_date', '')}.pdf"
    else:
        raise BadRequestException(
            "Invalid report_type. Use: daily | monthly | patient-history | doctor-summary"
        )

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
