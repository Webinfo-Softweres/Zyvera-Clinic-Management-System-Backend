from sqlalchemy.orm import Session
from typing import Any, Dict, Optional

from app.repositories.clinical_repository import clinical_repository
from app.repositories.patient_repository import patient_repository
from app.models.clinical_page import ClinicalPage
from app.core.exceptions import NotFoundException, BadRequestException

VALID_PAGES = set(range(1, 8))  # 1 – 7 inclusive


class ClinicalService:
    """Business logic for Clinical Pages and Case Aggregation."""

    # ── Validation ────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_page_no(page_no: int) -> None:
        if page_no not in VALID_PAGES:
            raise BadRequestException(
                f"Invalid page number '{page_no}'. Allowed values are 1–7."
            )

    @staticmethod
    def _validate_patient(db: Session, centre_code: str, hospital_no: str) -> None:
        patient = patient_repository.get_by_hospital_no(db, hospital_no, centre_code)
        if not patient:
            raise NotFoundException(
                f"Patient with hospital number '{hospital_no}' not found in this clinic."
            )

    # ── Save / Upsert ─────────────────────────────────────────────────────────

    @staticmethod
    def save_page(
        db: Session,
        centre_code: str,
        hospital_no: str,
        page_no: int,
        data: Dict[str, Any],
        user_id: str,
    ) -> ClinicalPage:
        ClinicalService._validate_page_no(page_no)
        ClinicalService._validate_patient(db, centre_code, hospital_no)
        return clinical_repository.upsert_page(
            db,
            centre_code=centre_code,
            hospital_no=hospital_no,
            page_no=page_no,
            page_data=data,
            user_id=user_id,
        )

    # ── Read ──────────────────────────────────────────────────────────────────

    @staticmethod
    def get_page(
        db: Session,
        centre_code: str,
        hospital_no: str,
        page_no: int,
    ) -> ClinicalPage:
        ClinicalService._validate_page_no(page_no)
        ClinicalService._validate_patient(db, centre_code, hospital_no)
        page = clinical_repository.get_page(db, centre_code, hospital_no, page_no)
        if not page:
            raise NotFoundException(
                f"Clinical page {page_no} not found for patient '{hospital_no}'."
            )
        return page

    # ── Update ────────────────────────────────────────────────────────────────

    @staticmethod
    def update_page(
        db: Session,
        centre_code: str,
        hospital_no: str,
        page_no: int,
        data: Dict[str, Any],
        user_id: str,
    ) -> ClinicalPage:
        ClinicalService._validate_page_no(page_no)
        ClinicalService._validate_patient(db, centre_code, hospital_no)
        page = clinical_repository.get_page(db, centre_code, hospital_no, page_no)
        if not page:
            raise NotFoundException(
                f"Clinical page {page_no} not found for patient '{hospital_no}'."
            )
        return clinical_repository.update_page(db, db_obj=page, page_data=data, user_id=user_id)

    # ── Case Aggregation ──────────────────────────────────────────────────────

    @staticmethod
    def get_case(db: Session, centre_code: str, hospital_no: str) -> Dict[str, Any]:
        """Return the full patient case: patient info + all 7 pages."""
        patient = patient_repository.get_by_hospital_no(db, hospital_no, centre_code)
        if not patient:
            raise NotFoundException(
                f"Patient with hospital number '{hospital_no}' not found."
            )

        pages = clinical_repository.get_all_pages_for_patient(db, centre_code, hospital_no)
        pages_map: Dict[int, Optional[Dict[str, Any]]] = {p.page_no: p.page_data for p in pages}

        return {
            "patient": {
                "id": patient.id,
                "centre_code": patient.centre_code,
                "hospital_no": patient.hospital_no,
                "reg_date": str(patient.reg_date) if patient.reg_date else None,
                "patient_name": patient.patient_name,
                "address": patient.address,
                "age": patient.age,
                "gender": patient.gender,
                "mobile": patient.mobile,
                "created_at": patient.created_at.isoformat(),
                "updated_at": patient.updated_at.isoformat(),
            },
            "page1": pages_map.get(1),
            "page2": pages_map.get(2),
            "page3": pages_map.get(3),
            "page4": pages_map.get(4),
            "page5": pages_map.get(5),
            "page6": pages_map.get(6),
            "page7": pages_map.get(7),
        }


clinical_service = ClinicalService()
