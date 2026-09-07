from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class PriceRecord(Base):
    """
    Registro histórico de precios para series de tiempo y detección de anomalías/descuentos.
    """
    __tablename__ = "price_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("supermarket_items.id", ondelete="CASCADE"), nullable=False, index=True)
    
    normal_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False) # CLP
    offer_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True) # CLP
    unit_price_normalized: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False) # Precio por kg o L
    is_offer: Mapped[bool] = mapped_column(Boolean, default=False)
    
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relación
    item = relationship("SupermarketItem", back_populates="price_records")
