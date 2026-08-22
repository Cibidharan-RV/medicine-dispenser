from pydantic import BaseModel, Field
from typing import Optional

class DoctorBase(BaseModel):
    medical_registration_number: str = Field(..., max_length=50)
    specialization: str = Field(..., max_length=100)

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    specialization: Optional[str] = Field(None, max_length=100)

class DoctorOut(DoctorBase):
    userid: int

    class Config:
        from_attributes = True
