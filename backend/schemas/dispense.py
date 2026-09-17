from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class DispenseLogBase(BaseModel):
    schedule_id: int
    dispense_datetime: datetime
    quantity_dispensed: int = Field(..., ge=0)
    status: str = Field(..., pattern="^(SUCCESS|FAILED|PARTIAL)$")
    failure_reason: Optional[str] = None

class DispenseLogCreate(DispenseLogBase):
    pass

class DispenseLogOut(DispenseLogBase):
    dispense_id: int

    class Config:
        from_attributes = True

class DispenseRequest(BaseModel):
    schedule_id: int
    nfc_uid: str
