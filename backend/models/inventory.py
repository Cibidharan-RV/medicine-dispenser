from sqlalchemy import Column, BigInteger, Integer, String, ForeignKeyConstraint, CheckConstraint
from backend.database import Base

class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        ForeignKeyConstraint(
            ["medicineid", "batchnumber"],
            ["medicine_batch.medicineid", "medicine_batch.batchnumber"],
            ondelete="RESTRICT"
        ),
        CheckConstraint("quantityavailable >= 0", name="chk_inventory_quantity"),
        CheckConstraint("minimumstocklevel >= 0", name="chk_inventory_minimum")
    )

    inventory_id = Column("inventoryid", BigInteger, primary_key=True, index=True)
    medicine_id = Column("medicineid", BigInteger, nullable=False)
    batch_number = Column("batchnumber", String(100), nullable=False)
    quantity_available = Column("quantityavailable", Integer, nullable=False)
    minimum_stock_level = Column("minimumstocklevel", Integer, nullable=False)
