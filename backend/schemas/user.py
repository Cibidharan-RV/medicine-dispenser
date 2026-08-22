from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., max_length=100)
    role: str = Field(..., pattern="^(PATIENT|DOCTOR|CAREGIVER)$")
    first_name: str = Field(..., max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: str = Field(..., max_length=50)
    phone_number: Optional[str] = Field(None, max_length=15)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    middle_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=15)
    password: Optional[str] = Field(None, min_length=6)

class UserOut(UserBase):
    userid: int

    class Config:
        from_attributes = True
