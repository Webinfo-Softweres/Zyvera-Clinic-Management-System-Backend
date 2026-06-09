from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.clinical_page import ClinicalPage
from app.repositories.base_repository import BaseRepository
from app.schemas.clinical_page import ClinicalPageCreate, ClinicalPageUpdate


class ClinicalRepository(BaseRepository[ClinicalPage, ClinicalPageCreate, ClinicalPageUpdate]):
    """Tenant-aware repository for ClinicalPage operations."""

    def get_page(
        self,
        db: Session,
        centre_code: str,
        hospital_no: str,
        page_no: int,
    ) -> Optional[ClinicalPage]:
        return (
            db.query(ClinicalPage)
            .filter(
                ClinicalPage.centre_code == centre_code,
                ClinicalPage.hospital_no == hospital_no,
                ClinicalPage.page_no == page_no,
            )
            .first()
        )

    def get_all_pages_for_patient(
        self,
        db: Session,
        centre_code: str,
        hospital_no: str,
    ) -> List[ClinicalPage]:
        return (
            db.query(ClinicalPage)
            .filter(
                ClinicalPage.centre_code == centre_code,
                ClinicalPage.hospital_no == hospital_no,
            )
            .order_by(ClinicalPage.page_no)
            .all()
        )

    def upsert_page(
        self,
        db: Session,
        centre_code: str,
        hospital_no: str,
        page_no: int,
        page_data: dict,
        user_id: str,
    ) -> ClinicalPage:
        """Create or update a clinical page (upsert)."""
        existing = self.get_page(db, centre_code, hospital_no, page_no)
        if existing:
            existing.page_data = page_data
            existing.updated_by = user_id
            db.commit()
            db.refresh(existing)
            return existing
        else:
            page = ClinicalPage(
                centre_code=centre_code,
                hospital_no=hospital_no,
                page_no=page_no,
                page_data=page_data,
                created_by=user_id,
                updated_by=user_id,
            )
            db.add(page)
            db.commit()
            db.refresh(page)
            return page

    def update_page(
        self,
        db: Session,
        db_obj: ClinicalPage,
        page_data: dict,
        user_id: str,
    ) -> ClinicalPage:
        db_obj.page_data = page_data
        db_obj.updated_by = user_id
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def count_pages_for_patient(
        self, db: Session, centre_code: str, hospital_no: str
    ) -> int:
        return (
            db.query(ClinicalPage)
            .filter(
                ClinicalPage.centre_code == centre_code,
                ClinicalPage.hospital_no == hospital_no,
            )
            .count()
        )


clinical_repository = ClinicalRepository(ClinicalPage)
