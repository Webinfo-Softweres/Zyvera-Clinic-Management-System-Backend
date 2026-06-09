from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(self.model).filter(
            self.model.username == username
        ).first()

    def get_multi_by_centre(self, db: Session, centre_code: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[User]:
        query = db.query(self.model)
        if centre_code:
            query = query.filter(self.model.centre_code == centre_code)
        return query.offset(skip).limit(limit).all()

    def create_user(self, db: Session, *, obj_in: dict) -> User:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repository = UserRepository(User)
