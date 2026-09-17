from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class MedicineBatchBase(BaseModel):
    batch_number: str = Field(..., max_length=100)
    medicine_id: int
    expiry_date: date

class MedicineBatchCreate(MedicineBatchBase):
    pass

class MedicineBatchOut(MedicineBatchBase):
    class Config:
        from_attributes = True

class InventoryBase(BaseModel):
    medicine_id: int
    batch_number: str = Field(..., max_length=100)
    quantity_available: int = Field(..., ge=0)
    minimum_stock_level: int = Field(..., ge=0)

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(BaseModel):
    quantity_available: Optional[int] = Field(None, ge=0)
    minimum_stock_level: Optional[int] = Field(None, ge=0)

class InventoryOut(InventoryBase):
    inventory_id: int
    expiry_date: Optional[date] = None

    class Config:
        from_attributes = True

class TopUpRequest(BaseModel):
    medicine_id: int
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2000, le=2100)
    quantity_to_add: int = Field(..., gt=0)
    minimum_stock_level: int = Field(10, ge=0)
