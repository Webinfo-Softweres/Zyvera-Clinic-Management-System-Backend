from sqlalchemy.orm import Session
from app.repositories.audit_repository import audit_repository, AuditLogCreate
from app.middleware.audit import request_context
from typing import Optional

class AuditService:
    @staticmethod
    def log_action(db: Session, action: str, module: str, record_id: Optional[str] = None):
        ctx = request_context.get()
        user_id = ctx.get("user_id")
        centre_code = ctx.get("centre_code")
        ip_address = ctx.get("ip_address")

        if not centre_code:
            return

        audit_in = AuditLogCreate(
            centre_code=centre_code,
            user_id=user_id,
            action=action,
            module=module,
            record_id=record_id,
            ip_address=ip_address
        )
        audit_repository.create(db=db, obj_in=audit_in)

    @staticmethod
    def log_action_explicit(db: Session, centre_code: str, action: str, module: str, user_id: Optional[str] = None, record_id: Optional[str] = None):
        ctx = request_context.get()
        ip_address = ctx.get("ip_address")

        audit_in = AuditLogCreate(
            centre_code=centre_code,
            user_id=user_id,
            action=action,
            module=module,
            record_id=record_id,
            ip_address=ip_address
        )
        audit_repository.create(db=db, obj_in=audit_in)

audit_service = AuditService()
