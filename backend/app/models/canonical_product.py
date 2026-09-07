from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class CanonicalProduct(Base):
    """
    Entidad canónica abstracta normalizada.
    Por ejemplo: 'Lomo Liso Vacuno' o 'Arroz Grado 1 1kg'.
    Agrupa los SKUs de los distintos supermercados (Lider, Jumbo, etc.)
    y almacena el vector de embedding semántico para búsqueda y deduplicación.
    """
    __tablename__ = "canonical_products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # carne_vacuno, leche, etc.
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # lomo_liso, entera, etc.
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    standard_unit: Mapped[str] = mapped_column(String(10), nullable=False) # 'kg' o 'L'
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Vector denso de 384 dimensiones para similitud semántica con pgvector
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(384), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    items = relationship("SupermarketItem", back_populates="canonical_product")
    alerts = relationship("UserAlert", back_populates="canonical_product", cascade="all, delete-orphan")
