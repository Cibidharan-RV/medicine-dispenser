from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from backend.auth.security import verify_password, create_access_token
from backend.database import get_db
from backend.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # The role claim is added for frontend convenience, but backend uses db user
    access_token = create_access_token(data={"sub": user.username, "role": user.role, "userid": user.userid})
    return Token(access_token=access_token)
