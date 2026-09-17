from pydantic import BaseModel, Field
from datetime import date, time
from typing import Optional

class DispenseScheduleBase(BaseModel):
    prescription_item_id: int
    scheduled_time: time
    quantity_to_dispense: int = Field(..., gt=0)
    start_date: date
    end_date: date

class DispenseScheduleCreate(DispenseScheduleBase):
    pass

class DispenseScheduleUpdate(BaseModel):
    scheduled_time: Optional[time] = None
    quantity_to_dispense: Optional[int] = Field(None, gt=0)
    end_date: Optional[date] = None

class DispenseScheduleOut(DispenseScheduleBase):
    schedule_id: int
    medicine_name: Optional[str] = None

    class Config:
        from_attributes = True
