from sqlalchemy.orm import Session
from datetime import date
from typing import Any, Dict

from app.repositories.report_repository import report_repository
from app.repositories.patient_repository import patient_repository
from app.core.exceptions import NotFoundException, BadRequestException


class ReportService:
    """Orchestrates report data and delegates PDF generation."""

    # ── Daily ─────────────────────────────────────────────────────────────────

    @staticmethod
    def get_daily_report(db: Session, centre_code: str, report_date: date) -> Dict[str, Any]:
        return report_repository.get_daily_stats(db, centre_code, report_date)

    # ── Monthly ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_monthly_report(
        db: Session, centre_code: str, month: int, year: int
    ) -> Dict[str, Any]:
        return report_repository.get_monthly_stats(db, centre_code, month, year)

    # ── Patient History ───────────────────────────────────────────────────────

    @staticmethod
    def get_patient_history(
        db: Session, centre_code: str, hospital_no: str
    ) -> Dict[str, Any]:
        result = report_repository.get_patient_history(db, centre_code, hospital_no)
        if result["patient"] is None:
            raise NotFoundException("Patient not found")
        return result

    # ── Doctor Summary ────────────────────────────────────────────────────────

    @staticmethod
    def get_doctor_summary(
        db: Session, centre_code: str, from_date: date, to_date: date
    ) -> Dict[str, Any]:
        if from_date > to_date:
            raise BadRequestException("from_date must be before or equal to to_date")
        return report_repository.get_doctor_summary(db, centre_code, from_date, to_date)

    # ── PDF Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def get_report_data_for_pdf(
        db: Session, centre_code: str, report_type: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect report data for PDF generation based on type."""
        if report_type == "daily":
            report_date = date.fromisoformat(params.get("date", str(date.today())))
            return report_repository.get_daily_stats(db, centre_code, report_date)

        elif report_type == "monthly":
            month = int(params.get("month", date.today().month))
            year = int(params.get("year", date.today().year))
            return report_repository.get_monthly_stats(db, centre_code, month, year)

        elif report_type == "patient-history":
            hospital_no = params.get("hospital_no")
            if not hospital_no:
                raise BadRequestException("hospital_no is required for patient-history report")
            result = report_repository.get_patient_history(db, centre_code, hospital_no)
            if result["patient"] is None:
                raise NotFoundException("Patient not found")
            return result

        elif report_type == "doctor-summary":
            from_date = date.fromisoformat(params.get("from_date", str(date.today())))
            to_date = date.fromisoformat(params.get("to_date", str(date.today())))
            return report_repository.get_doctor_summary(db, centre_code, from_date, to_date)

        else:
            raise BadRequestException(
                f"Unknown report type '{report_type}'. "
                "Valid types: daily, monthly, patient-history, doctor-summary"
            )


report_service = ReportService()
