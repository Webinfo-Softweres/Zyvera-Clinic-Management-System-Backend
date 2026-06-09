from sqlalchemy.orm import Session
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate, UserStatusUpdate
from typing import Optional
from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException
from app.core.security import hash_password
from app.utils.constants import USER_INACTIVE

from app.models.user import User

class UserService:
    @staticmethod
    def get_user(db: Session, user_id: str, centre_code: Optional[str] = None):
        user = user_repository.get(db, id=user_id)
        if not user or (centre_code and user.centre_code != centre_code):
            raise NotFoundException("User not found")
        return user

    @staticmethod
    def get_users(db: Session, centre_code: Optional[str] = None, skip: int = 0, limit: int = 100):
        return user_repository.get_multi_by_centre(db, centre_code=centre_code, skip=skip, limit=limit)

    @staticmethod
    def create_user(db: Session, user_in: UserCreate, creator: User):
        # Enforce Role Hierarchy
        if creator.role == "CLINIC_ADMIN":
            if user_in.role == "SUPER_ADMIN":
                raise ForbiddenException("Clinic Admins cannot create Super Admins")
            target_centre_code = creator.centre_code
        elif creator.role == "SUPER_ADMIN":
            if user_in.role != "SUPER_ADMIN" and not user_in.centre_code:
                raise ConflictException("centre_code is required when creating a clinic user")
            target_centre_code = user_in.centre_code
        else:
            raise ForbiddenException("Insufficient permissions to create user")

        existing_user = user_repository.get_by_username(db, user_in.username)
        if existing_user:
            raise ConflictException(detail="Username already exists")

        user_data = user_in.model_dump()
        user_data["password_hash"] = hash_password(user_data.pop("password"))
        user_data["centre_code"] = target_centre_code
        user_data["created_by"] = creator.id

        return user_repository.create_user(db, obj_in=user_data)

    @staticmethod
    def update_user(db: Session, user_id: str, centre_code: str, user_in: UserUpdate, updated_by: str = None):
        user = UserService.get_user(db, user_id, centre_code)
        update_data = user_in.model_dump(exclude_unset=True)
        if updated_by:
            update_data["updated_by"] = updated_by
            
        return user_repository.update(db, db_obj=user, obj_in=update_data)

    @staticmethod
    def delete_user(db: Session, user_id: str, centre_code: str, updated_by: str = None):
        user = UserService.get_user(db, user_id, centre_code)
        # Soft delete
        return user_repository.update(db, db_obj=user, obj_in={"status": USER_INACTIVE, "updated_by": updated_by})

user_service = UserService()
