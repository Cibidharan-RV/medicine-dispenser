from pydantic import BaseModel, Field
from typing import Optional

class DispenserSlotBase(BaseModel):
    slot_number: int
    capacity: int = Field(..., gt=0)

class DispenserSlotCreate(DispenserSlotBase):
    pass

class DispenserSlotUpdate(BaseModel):
    capacity: Optional[int] = Field(None, gt=0)

class DispenserSlotOut(DispenserSlotBase):
    slot_id: int

    class Config:
        from_attributes = True

class InventorySlotBase(BaseModel):
    inventory_id: int
    slot_id: int

class InventorySlotCreate(InventorySlotBase):
    pass

class InventorySlotOut(InventorySlotBase):
    class Config:
        from_attributes = True
