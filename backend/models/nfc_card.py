from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, text
from backend.database import Base

class NfcCard(Base):
    __tablename__ = "nfc_cards"

    card_id = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, ForeignKey("USER.userid", ondelete="CASCADE"), nullable=False)
    nfc_uid = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
