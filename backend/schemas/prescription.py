from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

class PrescriptionItemBase(BaseModel):
    medicine_id: int
    dosage: str = Field(..., max_length=100)
    frequency: str = Field(..., max_length=100)
    duration: str = Field(..., max_length=100)

class PrescriptionItemCreate(PrescriptionItemBase):
    pass

class PrescriptionItemOut(PrescriptionItemBase):
    prescription_item_id: int
    prescription_id: int

    class Config:
        from_attributes = True

class PrescriptionBase(BaseModel):
    patient_id: int
    doctor_id: int
    prescription_date: date
    start_date: date
    end_date: date

class PrescriptionCreate(PrescriptionBase):
    items: List[PrescriptionItemCreate]

class PrescriptionUpdate(BaseModel):
    end_date: Optional[date] = None

class PrescriptionOut(PrescriptionBase):
    prescription_id: int
    items: List[PrescriptionItemOut] = []

    class Config:
        from_attributes = True
