from pydantic import BaseModel, Field
from typing import Optional

class MedicineBase(BaseModel):
    medicine_name: str = Field(..., max_length=150)
    strength: str = Field(..., max_length=50)
    dosage_form: str = Field(..., max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=150)

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(BaseModel):
    medicine_name: Optional[str] = Field(None, max_length=150)
    strength: Optional[str] = Field(None, max_length=50)
    dosage_form: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=150)

class MedicineOut(MedicineBase):
    medicine_id: int

    class Config:
        from_attributes = True
