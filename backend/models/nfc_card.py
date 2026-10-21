from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, text
from backend.database import Base

class NfcCard(Base):
    __tablename__ = "nfc_card"

    card_id = Column("cardid", Integer, primary_key=True, index=True)
    userid = Column("userid", Integer, ForeignKey("USER.userid", ondelete="CASCADE"), nullable=False)
    nfc_uid = Column("nfcuid", String(255), unique=True, nullable=False)
    is_active = Column("isactive", Boolean, default=True)
    assigned_at = Column("assignedat", DateTime, server_default=text("CURRENT_TIMESTAMP"))
