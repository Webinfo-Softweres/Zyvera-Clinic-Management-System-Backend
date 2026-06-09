from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.repositories.base_repository import BaseRepository
from pydantic import BaseModel

class AuditLogCreate(BaseModel):
    centre_code: str
    user_id: Optional[str] = None
    action: str
    module: str
    record_id: Optional[str] = None
    ip_address: Optional[str] = None

class AuditRepository(BaseRepository[AuditLog, AuditLogCreate, AuditLogCreate]):
    def get_multi_by_centre(self, db: Session, centre_code: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        return db.query(self.model).filter(
            self.model.centre_code == centre_code
        ).order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

audit_repository = AuditRepository(AuditLog)
