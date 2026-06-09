from sqlalchemy.orm import Session
from app.models.clinic import Clinic
from app.schemas.clinic import ClinicCreate, ClinicUpdate
from app.repositories.base_repository import BaseRepository
from typing import Optional

class ClinicRepository(BaseRepository[Clinic, ClinicCreate, ClinicUpdate]):
    def get_by_centre_code(self, db: Session, centre_code: str) -> Optional[Clinic]:
        return db.query(self.model).filter(self.model.centre_code == centre_code).first()

    def create_clinic(self, db: Session, *, obj_in: dict) -> Clinic:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

clinic_repository = ClinicRepository(Clinic)
