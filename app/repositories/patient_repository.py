from sqlalchemy.orm import Session
from sqlalchemy import func, select, and_
from typing import List, Optional, Tuple
from datetime import date

from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientRepository(BaseRepository[Patient, PatientCreate, PatientUpdate]):
    """Tenant-aware repository for Patient operations."""

    # ── Hospital Number Generation ────────────────────────────────────────────

    def generate_hospital_no(self, db: Session, centre_code: str) -> str:
        """
        Atomically generate the next sequential hospital number for a centre.
        Format: HSP000001, HSP000002 …
        """
        # Lock the max number within this centre using FOR UPDATE (via with_for_update)
        stmt = (
            select(func.max(
                func.cast(func.substr(Patient.hospital_no, 4), func.Numeric())
            ))
            .where(Patient.centre_code == centre_code)
            .with_for_update()
        )
        result = db.execute(stmt).scalar()
        next_num = int(result) + 1 if result else 1
        return f"HSP{next_num:06d}"

    # ── Create ────────────────────────────────────────────────────────────────

    def create_patient(self, db: Session, *, obj_in: dict) -> Patient:
        patient = Patient(**obj_in)
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_by_id_and_centre(
        self, db: Session, patient_id: str, centre_code: str
    ) -> Optional[Patient]:
        return (
            db.query(Patient)
            .filter(
                Patient.id == patient_id,
                Patient.centre_code == centre_code,
                Patient.is_deleted == False,
            )
            .first()
        )

    def get_by_hospital_no(
        self, db: Session, hospital_no: str, centre_code: str
    ) -> Optional[Patient]:
        return (
            db.query(Patient)
            .filter(
                Patient.hospital_no == hospital_no,
                Patient.centre_code == centre_code,
                Patient.is_deleted == False,
            )
            .first()
        )

    def get_patients(
        self,
        db: Session,
        centre_code: str,
        skip: int = 0,
        limit: int = 20,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        patient_name: Optional[str] = None,
        mobile: Optional[str] = None,
        hospital_no: Optional[str] = None,
    ) -> Tuple[List[Patient], int]:
        query = db.query(Patient).filter(
            Patient.centre_code == centre_code,
            Patient.is_deleted == False,
        )

        if from_date:
            query = query.filter(Patient.reg_date >= from_date)
        if to_date:
            query = query.filter(Patient.reg_date <= to_date)
        if patient_name:
            query = query.filter(Patient.patient_name.ilike(f"%{patient_name}%"))
        if mobile:
            query = query.filter(Patient.mobile.ilike(f"%{mobile}%"))
        if hospital_no:
            query = query.filter(Patient.hospital_no.ilike(f"%{hospital_no}%"))

        total = query.count()
        items = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    def search_patients(
        self,
        db: Session,
        centre_code: str,
        q: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Patient], int]:
        """Full text LIKE search across hospital_no, mobile, and patient_name."""
        query = db.query(Patient).filter(
            Patient.centre_code == centre_code,
            Patient.is_deleted == False,
        ).filter(
            (Patient.hospital_no.ilike(f"%{q}%"))
            | (Patient.mobile.ilike(f"%{q}%"))
            | (Patient.patient_name.ilike(f"%{q}%"))
        )
        total = query.count()
        items = query.order_by(Patient.patient_name).offset(skip).limit(limit).all()
        return items, total

    # ── Update ────────────────────────────────────────────────────────────────

    def update_patient(self, db: Session, *, db_obj: Patient, update_data: dict) -> Patient:
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # ── Soft Delete ───────────────────────────────────────────────────────────

    def soft_delete(self, db: Session, *, db_obj: Patient, deleted_by: str) -> Patient:
        from datetime import datetime, timezone
        db_obj.is_deleted = True
        db_obj.deleted_at = datetime.now(timezone.utc)
        db_obj.updated_by = deleted_by
        db.commit()
        db.refresh(db_obj)
        return db_obj


patient_repository = PatientRepository(Patient)
