from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey, CheckConstraint
from backend.database import Base

class DispenseLog(Base):
    __tablename__ = "DISPENSE_LOG"
    __table_args__ = (
        CheckConstraint("quantitydispensed >= 0", name="chk_dispense_quantity"),
        CheckConstraint("status IN ('SUCCESS', 'FAILED', 'PARTIAL')", name="chk_dispense_status")
    )

    dispense_id = Column("dispenseid", BigInteger, primary_key=True, index=True)
    schedule_id = Column("scheduleid", BigInteger, ForeignKey("DISPENSE_SCHEDULE.scheduleid", ondelete="CASCADE"), nullable=False)
    dispense_datetime = Column("dispensedatetime", DateTime(timezone=True), nullable=False)
    quantity_dispensed = Column("quantitydispensed", Integer, nullable=False)
    status = Column("status", String(20), nullable=False)
    failure_reason = Column("failurereason", String)
