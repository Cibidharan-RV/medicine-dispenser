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

    class Config:
        from_attributes = True
