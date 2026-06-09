from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date

from app.models.patient import Patient
from app.models.clinical_page import ClinicalPage


class ReportRepository:
    """Optimised reporting queries — all tenant-scoped, no N+1."""

    # ── Daily Report ──────────────────────────────────────────────────────────

    def get_daily_stats(
        self, db: Session, centre_code: str, report_date: date
    ) -> dict:
        total = (
            db.query(func.count(Patient.id))
            .filter(
                Patient.centre_code == centre_code,
                Patient.reg_date == report_date,
                Patient.is_deleted == False,
            )
            .scalar()
        ) or 0

        return {
            "report_date": report_date,
            "total_registrations": total,
            "new_patients": total,  # every registration on that day is a new patient
            "centre_code": centre_code,
        }

    # ── Monthly Report ────────────────────────────────────────────────────────

    def get_monthly_stats(
        self, db: Session, centre_code: str, month: int, year: int
    ) -> dict:
        rows = (
            db.query(
                Patient.reg_date,
                func.count(Patient.id).label("registrations"),
            )
            .filter(
                Patient.centre_code == centre_code,
                func.month(Patient.reg_date) == month,
                func.year(Patient.reg_date) == year,
                Patient.is_deleted == False,
            )
            .group_by(Patient.reg_date)
            .order_by(Patient.reg_date)
            .all()
        )

        daily_breakdown = [
            {"report_date": r.reg_date, "registrations": r.registrations}
            for r in rows
        ]
        monthly_total = sum(r["registrations"] for r in daily_breakdown)

        return {
            "month": month,
            "year": year,
            "centre_code": centre_code,
            "monthly_total": monthly_total,
            "daily_breakdown": daily_breakdown,
        }

    # ── Patient History ───────────────────────────────────────────────────────

    def get_patient_history(
        self, db: Session, centre_code: str, hospital_no: str
    ) -> dict:
        patient = (
            db.query(Patient)
            .filter(
                Patient.centre_code == centre_code,
                Patient.hospital_no == hospital_no,
                Patient.is_deleted == False,
            )
            .first()
        )

        pages = (
            db.query(ClinicalPage)
            .filter(
                ClinicalPage.centre_code == centre_code,
                ClinicalPage.hospital_no == hospital_no,
            )
            .order_by(ClinicalPage.page_no)
            .all()
        )

        timeline = [
            {
                "event": f"Page {p.page_no} {'created' if p.created_at == p.updated_at else 'updated'}",
                "page_no": p.page_no,
                "timestamp": p.updated_at.isoformat(),
            }
            for p in pages
        ]

        return {
            "patient": patient,
            "clinical_pages": pages,
            "timeline": timeline,
        }

    # ── Doctor Summary ────────────────────────────────────────────────────────

    def get_doctor_summary(
        self,
        db: Session,
        centre_code: str,
        from_date: date,
        to_date: date,
    ) -> dict:
        patients_seen = (
            db.query(func.count(Patient.id))
            .filter(
                Patient.centre_code == centre_code,
                Patient.reg_date >= from_date,
                Patient.reg_date <= to_date,
                Patient.is_deleted == False,
            )
            .scalar()
        ) or 0

        # Distinct hospital_nos that have at least one clinical page in range
        cases_created = (
            db.query(func.count(func.distinct(ClinicalPage.hospital_no)))
            .filter(
                ClinicalPage.centre_code == centre_code,
                func.date(ClinicalPage.created_at) >= from_date,
                func.date(ClinicalPage.created_at) <= to_date,
            )
            .scalar()
        ) or 0

        clinical_records = (
            db.query(func.count(ClinicalPage.id))
            .filter(
                ClinicalPage.centre_code == centre_code,
                func.date(ClinicalPage.created_at) >= from_date,
                func.date(ClinicalPage.created_at) <= to_date,
            )
            .scalar()
        ) or 0

        return {
            "centre_code": centre_code,
            "from_date": from_date,
            "to_date": to_date,
            "patients_seen": patients_seen,
            "cases_created": cases_created,
            "clinical_records_entered": clinical_records,
        }


report_repository = ReportRepository()
