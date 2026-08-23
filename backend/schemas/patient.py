from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class PatientBase(BaseModel):
    date_of_birth: date
    gender: Optional[str] = Field(None, max_length=20)
    street: Optional[str] = Field(None, max_length=150)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    street: Optional[str] = Field(None, max_length=150)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)

class PatientOut(PatientBase):
    userid: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True
