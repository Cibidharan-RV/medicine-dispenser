from sqlalchemy import Column, BigInteger, Integer, CheckConstraint
from backend.database import Base

class DispenserSlot(Base):
    __tablename__ = "dispenser_slot"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="chk_slot_capacity"),
    )

    slot_id = Column("slotid", BigInteger, primary_key=True, index=True)
    slot_number = Column("slotnumber", Integer, unique=True, nullable=False)
    capacity = Column("capacity", Integer, nullable=False)
