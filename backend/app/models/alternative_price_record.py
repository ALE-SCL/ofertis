from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AlternativePriceRecord(Base):
    """
    Registro histórico de precios para canales alternativos y mayoristas.
    Permite trazar la evolución del spread frente al retail tradicional.
    """
    __tablename__ = "alternative_price_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("alternative_items.id", ondelete="CASCADE"), nullable=False, index=True)
    
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price_normalized: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    traditional_benchmark_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    savings_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relación
    item = relationship("AlternativeItem", back_populates="price_records")
