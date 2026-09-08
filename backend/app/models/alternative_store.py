from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class AlternativeStore(Base):
    """
    Representa un supermercado mayorista o canal alternativo independiente
    (ej: Alvi, Central Mayorista, Doña Carne, El Carnicero, Lo Valledor, etc.)
    """
    __tablename__ = "alternative_stores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    store_type: Mapped[str] = mapped_column(String(50), nullable=False)
    type_label: Mapped[str] = mapped_column(String(100), nullable=False)
    badge_color: Mapped[str] = mapped_column(String(20), default="blue")
    website: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    coverage: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    highlight: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    items = relationship("AlternativeItem", back_populates="store", cascade="all, delete-orphan")
