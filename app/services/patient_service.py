from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import date, datetime, timezone

from app.repositories.patient_repository import patient_repository
from app.schemas.patient import PatientCreate, PatientUpdate
from app.models.patient import Patient
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException


class PatientService:
    """Business logic for Patient module."""

    # ── Create ────────────────────────────────────────────────────────────────

    @staticmethod
    def create_patient(
        db: Session, patient_in: PatientCreate, centre_code: str, created_by: str
    ) -> Patient:
        hospital_no = patient_repository.generate_hospital_no(db, centre_code)
        reg_date = patient_in.reg_date or datetime.now(timezone.utc).date()

        obj_in = {
            "centre_code": centre_code,
            "hospital_no": hospital_no,
            "reg_date": reg_date,
            "patient_name": patient_in.patient_name,
            "address": patient_in.address,
            "age": patient_in.age,
            "gender": patient_in.gender,
            "mobile": patient_in.mobile,
            "created_by": created_by,
            "updated_by": created_by,
        }
        return patient_repository.create_patient(db, obj_in=obj_in)

    # ── Read ──────────────────────────────────────────────────────────────────

    @staticmethod
    def get_patient(db: Session, patient_id: str, centre_code: str) -> Patient:
        patient = patient_repository.get_by_id_and_centre(db, patient_id, centre_code)
        if not patient:
            raise NotFoundException("Patient not found")
        return patient

    @staticmethod
    def get_patient_by_hospital_no(
        db: Session, hospital_no: str, centre_code: str
    ) -> Patient:
        patient = patient_repository.get_by_hospital_no(db, hospital_no, centre_code)
        if not patient:
            raise NotFoundException("Patient not found")
        return patient

    @staticmethod
    def list_patients(
        db: Session,
        centre_code: str,
        page: int = 1,
        size: int = 20,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        patient_name: Optional[str] = None,
        mobile: Optional[str] = None,
        hospital_no: Optional[str] = None,
    ) -> Tuple[List[Patient], int]:
        skip = (page - 1) * size
        return patient_repository.get_patients(
            db,
            centre_code=centre_code,
            skip=skip,
            limit=size,
            from_date=from_date,
            to_date=to_date,
            patient_name=patient_name,
            mobile=mobile,
            hospital_no=hospital_no,
        )

    @staticmethod
    def search_patients(
        db: Session,
        centre_code: str,
        q: str,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[Patient], int]:
        if not q or len(q.strip()) < 2:
            raise BadRequestException("Search query must be at least 2 characters")
        skip = (page - 1) * size
        return patient_repository.search_patients(
            db, centre_code=centre_code, q=q.strip(), skip=skip, limit=size
        )

    # ── Update ────────────────────────────────────────────────────────────────

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: str,
        centre_code: str,
        patient_in: PatientUpdate,
        updated_by: str,
    ) -> Patient:
        patient = PatientService.get_patient(db, patient_id, centre_code)
        update_data = patient_in.model_dump(exclude_unset=True)
        # Immutable fields guard
        for immutable in ("hospital_no", "centre_code", "created_at"):
            update_data.pop(immutable, None)
        update_data["updated_by"] = updated_by
        return patient_repository.update_patient(db, db_obj=patient, update_data=update_data)

    # ── Soft Delete ───────────────────────────────────────────────────────────

    @staticmethod
    def delete_patient(
        db: Session, patient_id: str, centre_code: str, deleted_by: str
    ) -> Patient:
        patient = PatientService.get_patient(db, patient_id, centre_code)
        return patient_repository.soft_delete(db, db_obj=patient, deleted_by=deleted_by)


patient_service = PatientService()
