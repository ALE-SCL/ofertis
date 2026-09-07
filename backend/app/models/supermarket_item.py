from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Boolean, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SupermarketItem(Base):
    """
    Representa un SKU real de un supermercado específico.
    Ej: 'Posta Negra Vacuno Granel' en Lider con SKU '12345'.
    """
    __tablename__ = "supermarket_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    canonical_id: Mapped[Optional[int]] = mapped_column(ForeignKey("canonical_products.id", ondelete="SET NULL"), nullable=True, index=True)
    supermarket_id: Mapped[int] = mapped_column(ForeignKey("supermarkets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    store_title: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_extracted: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    product_url: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    package_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False) # ej: 0.400 para 400g, 1.000 para 1kg
    package_unit: Mapped[str] = mapped_column(String(10), nullable=False) # 'kg', 'g', 'L', 'ml'
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    canonical_product = relationship("CanonicalProduct", back_populates="items")
    supermarket = relationship("Supermarket", back_populates="items")
    price_records = relationship("PriceRecord", back_populates="item", cascade="all, delete-orphan", order_by="desc(PriceRecord.recorded_at)")

    __table_args__ = (
        UniqueConstraint("supermarket_id", "sku", name="uq_supermarket_sku"),
    )
