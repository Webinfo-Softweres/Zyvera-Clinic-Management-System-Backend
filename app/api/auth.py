from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, ChangePasswordRequest, RefreshTokenRequest
from app.schemas.common import SuccessResponse
from app.services.auth_service import auth_service
from app.services.audit_service import audit_service
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.utils.constants import USER_ACTIVE

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    result = auth_service.login(db, login_data)
    # The payload 'sub' is the user_id. Need to decode to log action explicitly
    payload = decode_token(result.access_token)
    audit_centre_code = result.centre_code or "SYSTEM"
    audit_service.log_action_explicit(db, centre_code=audit_centre_code, action="LOGIN", module="Auth", user_id=payload.get("sub"))
    return result

@router.post("/refresh-token", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedException("Invalid refresh token")
    
    user_id = payload.get("sub")
    centre_code = payload.get("centre_code")
    role = payload.get("role")
    
    access_token = create_access_token(data={"sub": user_id, "centre_code": centre_code, "role": role})
    new_refresh_token = create_refresh_token(data={"sub": user_id, "centre_code": centre_code, "role": role})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        role=role,
        centre_code=centre_code
    )

@router.post("/change-password", response_model=SuccessResponse)
def change_password(password_data: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    auth_service.change_password(db, current_user.id, current_user.centre_code, password_data)
    audit_service.log_action(db, action="CHANGE_PASSWORD", module="Auth", record_id=current_user.id)
    return SuccessResponse(message="Password changed successfully")

@router.post("/logout", response_model=SuccessResponse)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    audit_service.log_action(db, action="LOGOUT", module="Auth", record_id=current_user.id)
    return SuccessResponse(message="Logged out successfully")
