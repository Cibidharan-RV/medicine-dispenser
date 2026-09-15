from sqlalchemy import Column, BigInteger, ForeignKey
from backend.database import Base

class InventorySlot(Base):
    __tablename__ = "inventory_slot"

    inventory_id = Column("inventoryid", BigInteger, ForeignKey("inventory.inventoryid", ondelete="CASCADE"), primary_key=True)
    slot_id = Column("slotid", BigInteger, ForeignKey("dispenser_slot.slotid", ondelete="RESTRICT"), unique=True, nullable=False)
