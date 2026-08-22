from sqlalchemy import Column, BigInteger, ForeignKey
from backend.database import Base

class InventorySlot(Base):
    __tablename__ = "INVENTORY_SLOT"

    inventory_id = Column("inventoryid", BigInteger, ForeignKey("INVENTORY.inventoryid", ondelete="CASCADE"), primary_key=True)
    slot_id = Column("slotid", BigInteger, ForeignKey("DISPENSER_SLOT.slotid", ondelete="RESTRICT"), unique=True, nullable=False)
