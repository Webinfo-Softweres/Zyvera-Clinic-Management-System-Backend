from fastapi import Depends
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.core.exceptions import ForbiddenException
from app.utils.constants import SUPER_ADMIN, CLINIC_ADMIN, CLINIC_USER

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != SUPER_ADMIN:
        raise ForbiddenException("Super Admin access required")
    return current_user

def require_clinic_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [SUPER_ADMIN, CLINIC_ADMIN]:
        raise ForbiddenException("Clinic Admin access required")
    return current_user

def require_admin_roles(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in [SUPER_ADMIN, CLINIC_ADMIN]:
        raise ForbiddenException("Admin role required")
    return current_user

from fastapi import Depends, Query
from typing import Optional

def get_current_tenant(
    current_user: User = Depends(get_current_user),
    centre_code: Optional[str] = Query(None, description="Required for Super Admins to specify a clinic")
) -> Optional[str]:
    if current_user.role == SUPER_ADMIN:
        return centre_code
    return current_user.centre_code

def get_current_clinic_admin(current_user: User = Depends(require_clinic_admin)) -> User:
    return current_user

def get_super_admin(current_user: User = Depends(require_super_admin)) -> User:
    return current_user
