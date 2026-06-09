from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException(detail="Could not validate credentials")
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="Could not validate credentials")
        
    token_type: str = payload.get("type")
    if token_type != "access":
        raise UnauthorizedException(detail="Invalid token type")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedException(detail="User not found")
        
    return user
