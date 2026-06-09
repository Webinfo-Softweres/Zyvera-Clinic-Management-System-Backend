from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.schemas.common import SuccessResponse, PaginatedResponse
from app.services.patient_service import patient_service
from app.services.audit_service import audit_service
from app.dependencies.auth import get_current_user
from app.dependencies.tenant import require_clinic_admin
from app.models.user import User

router = APIRouter(tags=["Patients"])


@router.post(
    "",
    response_model=SuccessResponse[PatientResponse],
    summary="Register a new patient",
    description=(
        "Creates a new patient record. Hospital number is auto-generated "
        "sequentially per clinic (e.g. HSP000001). centre_code is taken "
        "from the authenticated user's token — never from the request body."
    ),
)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    patient = patient_service.create_patient(
        db,
        patient_in=patient_in,
        centre_code=current_user.centre_code,
        created_by=str(current_user.id),
    )
    audit_service.log_action(db, action="CREATE_PATIENT", module="Patients", record_id=patient.id)
    return SuccessResponse(message="Patient registered successfully", data=patient)


@router.get(
    "",
    response_model=PaginatedResponse[PatientResponse],
    summary="List patients with filters and pagination",
    description=(
        "Returns a paginated list of patients for the authenticated clinic. "
        "Supports filtering by date range, name, mobile, and hospital number."
    ),
)
def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Records per page"),
    from_date: Optional[date] = Query(None, description="Filter from registration date"),
    to_date: Optional[date] = Query(None, description="Filter to registration date"),
    patient_name: Optional[str] = Query(None, description="Partial match on patient name"),
    mobile: Optional[str] = Query(None, description="Partial match on mobile number"),
    hospital_no: Optional[str] = Query(None, description="Partial match on hospital number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = patient_service.list_patients(
        db,
        centre_code=current_user.centre_code,
        page=page,
        size=size,
        from_date=from_date,
        to_date=to_date,
        patient_name=patient_name,
        mobile=mobile,
        hospital_no=hospital_no,
    )
    return PaginatedResponse(items=items, page=page, size=size, total=total)


@router.get(
    "/search",
    response_model=PaginatedResponse[PatientResponse],
    summary="Search patients",
    description=(
        "Full-text LIKE search across hospital number, mobile, and patient name. "
        "Results are scoped to the authenticated clinic."
    ),
)
def search_patients(
    q: str = Query(..., min_length=2, description="Search term (hospital_no / mobile / name)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = patient_service.search_patients(
        db,
        centre_code=current_user.centre_code,
        q=q,
        page=page,
        size=size,
    )
    return PaginatedResponse(items=items, page=page, size=size, total=total)


@router.get(
    "/{patient_id}",
    response_model=SuccessResponse[PatientResponse],
    summary="Get a single patient by ID",
)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = patient_service.get_patient(
        db, patient_id=patient_id, centre_code=current_user.centre_code
    )
    return SuccessResponse(data=patient)


@router.put(
    "/{patient_id}",
    response_model=SuccessResponse[PatientResponse],
    summary="Update patient details",
    description=(
        "Updates editable fields. hospital_no, centre_code, and created_at "
        "are immutable and will be ignored even if provided."
    ),
)
def update_patient(
    patient_id: str,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = patient_service.update_patient(
        db,
        patient_id=patient_id,
        centre_code=current_user.centre_code,
        patient_in=patient_in,
        updated_by=str(current_user.id),
    )
    audit_service.log_action(db, action="UPDATE_PATIENT", module="Patients", record_id=patient.id)
    return SuccessResponse(message="Patient updated successfully", data=patient)


@router.delete(
    "/{patient_id}",
    response_model=SuccessResponse[PatientResponse],
    summary="Soft-delete a patient",
    description="Marks the patient as deleted (is_deleted=True). No data is permanently removed.",
)
def delete_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_clinic_admin),
):
    patient = patient_service.delete_patient(
        db,
        patient_id=patient_id,
        centre_code=current_user.centre_code,
        deleted_by=str(current_user.id),
    )
    audit_service.log_action(db, action="DELETE_PATIENT", module="Patients", record_id=patient.id)
    return SuccessResponse(message="Patient deleted successfully", data=patient)
