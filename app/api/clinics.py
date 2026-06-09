from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicResponse, ClinicStatusUpdate
from app.schemas.common import SuccessResponse, PaginatedResponse
from app.services.clinic_service import clinic_service
from app.services.audit_service import audit_service
from app.dependencies.tenant import require_super_admin
from app.models.user import User

router = APIRouter(tags=["Clinics"])

@router.get("", response_model=PaginatedResponse[ClinicResponse])
def get_clinics(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    skip = (page - 1) * size
    clinics = clinic_service.get_clinics(db, skip=skip, limit=size)
    total = len(clinics) # Note: For a production app, use a proper COUNT query
    return PaginatedResponse(items=clinics, page=page, size=size, total=total)

@router.post("", response_model=SuccessResponse[dict])
def create_clinic(clinic_in: ClinicCreate, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    clinic, admin_username, admin_password = clinic_service.create_clinic(db, clinic_in, created_by=current_user.id)
    audit_service.log_action(db, action="CREATE_CLINIC", module="Clinics", record_id=clinic.id)
    
    return SuccessResponse(
        message="Clinic created successfully",
        data={
            "clinic_id": clinic.id,
            "centre_code": clinic.centre_code,
            "admin_credentials": {
                "username": admin_username,
                "password": admin_password
            }
        }
    )

@router.get("/{clinic_id}", response_model=SuccessResponse[ClinicResponse])
def get_clinic(clinic_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    clinic = clinic_service.get_clinic(db, clinic_id)
    return SuccessResponse(data=clinic)

@router.put("/{clinic_id}", response_model=SuccessResponse[ClinicResponse])
def update_clinic(clinic_id: str, clinic_in: ClinicUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    clinic = clinic_service.update_clinic(db, clinic_id, clinic_in, updated_by=current_user.id)
    audit_service.log_action(db, action="UPDATE_CLINIC", module="Clinics", record_id=clinic.id)
    return SuccessResponse(message="Clinic updated successfully", data=clinic)

@router.patch("/{clinic_id}/status", response_model=SuccessResponse[ClinicResponse])
def update_clinic_status(clinic_id: str, status_in: ClinicStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_super_admin)):
    clinic = clinic_service.update_status(db, clinic_id, status_in, updated_by=current_user.id)
    audit_service.log_action(db, action="UPDATE_CLINIC_STATUS", module="Clinics", record_id=clinic.id)
    return SuccessResponse(message="Clinic status updated successfully", data=clinic)
