from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import SuccessResponse, PaginatedResponse
from app.services.user_service import user_service
from app.services.audit_service import audit_service
from app.dependencies.tenant import get_current_tenant, require_clinic_admin
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.exceptions import ForbiddenException

router = APIRouter(tags=["Users"])

from typing import Optional

@router.get("", response_model=PaginatedResponse[UserResponse])
def get_users(
    page: int = Query(1, ge=1), 
    size: int = Query(20, ge=1, le=100), 
    db: Session = Depends(get_db), 
    centre_code: Optional[str] = Depends(get_current_tenant),
    current_user: User = Depends(require_clinic_admin)
):
    skip = (page - 1) * size
    users = user_service.get_users(db, centre_code=centre_code, skip=skip, limit=size)
    total = len(users)
    return PaginatedResponse(items=users, page=page, size=size, total=total)

@router.post("", response_model=SuccessResponse[UserResponse])
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_clinic_admin)
):
    user = user_service.create_user(db, user_in=user_in, creator=current_user)
    audit_service.log_action(db, action="CREATE_USER", module="Users", record_id=user.id)
    return SuccessResponse(message="User created successfully", data=user)

@router.get("/{user_id}", response_model=SuccessResponse[UserResponse])
def get_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    centre_code: str = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "CLINIC_USER" and current_user.id != user_id:
        raise ForbiddenException("You can only view your own profile")
        
    user = user_service.get_user(db, user_id, centre_code)
    return SuccessResponse(data=user)

@router.put("/{user_id}", response_model=SuccessResponse[UserResponse])
def update_user(
    user_id: str, 
    user_in: UserUpdate, 
    db: Session = Depends(get_db), 
    centre_code: str = Depends(get_current_tenant),
    current_user: User = Depends(require_clinic_admin)
):
    user = user_service.update_user(db, user_id, centre_code, user_in, updated_by=current_user.id)
    audit_service.log_action(db, action="UPDATE_USER", module="Users", record_id=user.id)
    return SuccessResponse(message="User updated successfully", data=user)

@router.delete("/{user_id}", response_model=SuccessResponse[UserResponse])
def delete_user(
    user_id: str, 
    db: Session = Depends(get_db), 
    centre_code: str = Depends(get_current_tenant),
    current_user: User = Depends(require_clinic_admin)
):
    user = user_service.delete_user(db, user_id, centre_code, updated_by=current_user.id)
    audit_service.log_action(db, action="DELETE_USER", module="Users", record_id=user.id)
    return SuccessResponse(message="User deleted successfully", data=user)
