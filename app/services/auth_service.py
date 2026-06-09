from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, TokenResponse, ChangePasswordRequest
from app.repositories.user_repository import user_repository
from app.repositories.clinic_repository import clinic_repository
from app.core.exceptions import UnauthorizedException, BadRequestException
from app.core.security import verify_password, create_access_token, create_refresh_token, hash_password
from app.utils.constants import USER_ACTIVE, CLINIC_ACTIVE
from datetime import date

class AuthService:
    @staticmethod
    def login(db: Session, login_data: LoginRequest) -> TokenResponse:
        user = user_repository.get_by_username(db, login_data.username)
        if not user:
            raise UnauthorizedException("Invalid credentials")

        if not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedException("Invalid credentials")

        if user.status != USER_ACTIVE:
            raise UnauthorizedException("User account is not active")

        if user.role != "SUPER_ADMIN":
            if login_data.centre_code != user.centre_code:
                raise UnauthorizedException("Invalid credentials")
                
            clinic = clinic_repository.get_by_centre_code(db, user.centre_code)
            if not clinic or clinic.status != CLINIC_ACTIVE:
                raise UnauthorizedException("Clinic is not active")

            if clinic.license_expiry and clinic.license_expiry < date.today():
                raise UnauthorizedException("Clinic license has expired")

        access_token = create_access_token(data={"sub": user.id, "centre_code": user.centre_code, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": user.id, "centre_code": user.centre_code, "role": user.role})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            role=user.role,
            centre_code=user.centre_code
        )

    @staticmethod
    def change_password(db: Session, user_id: str, centre_code: str, password_data: ChangePasswordRequest):
        user = user_repository.get(db, id=user_id)
        if not user or user.centre_code != centre_code:
            raise UnauthorizedException("User not found")

        if not verify_password(password_data.old_password, user.password_hash):
            raise BadRequestException("Incorrect old password")

        new_password_hash = hash_password(password_data.new_password)
        user_repository.update(db, db_obj=user, obj_in={"password_hash": new_password_hash})

auth_service = AuthService()
