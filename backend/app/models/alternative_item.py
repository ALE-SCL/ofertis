from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Boolean, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class AlternativeItem(Base):
    """
    Representa un producto u oportunidad en un canal alternativo / mayorista
    con cálculo de benchmark de retail tradicional y embedding semántico pgvector.
    """
    __tablename__ = "alternative_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("alternative_stores.id", ondelete="CASCADE"), nullable=False, index=True)
    
    sku: Mapped[str] = mapped_column(String(150), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    unit: Mapped[str] = mapped_column(String(100), nullable=False)
    
    package_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3), default=1.000)
    package_unit: Mapped[str] = mapped_column(String(10), default="kg")
    
    current_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    unit_price_normalized: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    
    benchmark_category_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    traditional_benchmark_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    benchmark_label: Mapped[str] = mapped_column(String(150), nullable=False)
    savings_clp: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    savings_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    
    deal_level: Mapped[str] = mapped_column(String(50), nullable=False)
    deal_label: Mapped[str] = mapped_column(String(100), nullable=False)
    is_wholesale: Mapped[bool] = mapped_column(Boolean, default=False)
    purchase_url: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(384), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    store = relationship("AlternativeStore", back_populates="items")
    price_records = relationship(
        "AlternativePriceRecord",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="desc(AlternativePriceRecord.recorded_at)"
    )

    __table_args__ = (
        UniqueConstraint("store_id", "sku", name="uq_alternative_store_sku"),
    )
