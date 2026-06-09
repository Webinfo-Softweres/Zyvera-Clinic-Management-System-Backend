from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.core.database import get_db
from app.schemas.clinical_page import (
    ClinicalPageCreate,
    ClinicalPageUpdate,
    ClinicalPageResponse,
    CaseAggregateResponse,
)
from app.schemas.common import SuccessResponse
from app.services.clinical_service import clinical_service
from app.services.audit_service import audit_service
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Clinical"])


# ── Clinical Pages ────────────────────────────────────────────────────────────

@router.post(
    "/page/{page_no}",
    response_model=SuccessResponse[ClinicalPageResponse],
    summary="Save (upsert) a clinical page",
    description=(
        "Creates or updates a clinical page for a patient. "
        "page_no must be 1–7. Patient must belong to the authenticated clinic. "
        "If the page already exists, its JSON data is replaced."
    ),
)
def save_clinical_page(
    page_no: int,
    payload: ClinicalPageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page = clinical_service.save_page(
        db,
        centre_code=current_user.centre_code,
        hospital_no=payload.hospital_no,
        page_no=page_no,
        data=payload.data,
        user_id=str(current_user.id),
    )
    audit_service.log_action(db, action="SAVE_CLINICAL_PAGE", module="Clinical", record_id=page.id)
    return SuccessResponse(message=f"Clinical page {page_no} saved successfully", data=page)


@router.get(
    "/page/{page_no}",
    response_model=SuccessResponse[ClinicalPageResponse],
    summary="Retrieve a clinical page",
    description="Fetches a specific clinical page (1–7) for the given hospital_no.",
)
def get_clinical_page(
    page_no: int,
    hospital_no: str = Query(..., description="Patient hospital number, e.g. HSP000001"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page = clinical_service.get_page(
        db,
        centre_code=current_user.centre_code,
        hospital_no=hospital_no,
        page_no=page_no,
    )
    return SuccessResponse(data=page)


@router.put(
    "/page/{page_no}",
    response_model=SuccessResponse[ClinicalPageResponse],
    summary="Update a clinical page",
    description=(
        "Replaces the JSON data of an existing clinical page. "
        "The page must already exist; use POST to create."
    ),
)
def update_clinical_page(
    page_no: int,
    payload: ClinicalPageUpdate,
    hospital_no: str = Query(..., description="Patient hospital number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    page = clinical_service.update_page(
        db,
        centre_code=current_user.centre_code,
        hospital_no=hospital_no,
        page_no=page_no,
        data=payload.data,
        user_id=str(current_user.id),
    )
    audit_service.log_action(db, action="UPDATE_CLINICAL_PAGE", module="Clinical", record_id=page.id)
    return SuccessResponse(message=f"Clinical page {page_no} updated successfully", data=page)


# ── Case Aggregation ──────────────────────────────────────────────────────────

@router.get(
    "/case/{hospital_no}",
    response_model=SuccessResponse[CaseAggregateResponse],
    summary="Get complete patient case",
    description=(
        "Returns the patient record plus all clinical pages (1–7) in a single response. "
        "Pages that have not been filled will be null. Tenant isolation is enforced."
    ),
)
def get_case(
    hospital_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = clinical_service.get_case(
        db,
        centre_code=current_user.centre_code,
        hospital_no=hospital_no,
    )
    return SuccessResponse(data=case)
