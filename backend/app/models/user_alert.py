from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserAlert(Base):
    """
    Reglas de alertas suscritas por los usuarios para recibir notificaciones por WhatsApp.
    """
    __tablename__ = "user_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_phone: Mapped[str] = mapped_column(String(25), nullable=False, index=True) # E.164 (+569...)
    user_name: Mapped[str] = mapped_column(String(100), default="Usuario")
    canonical_id: Mapped[int] = mapped_column(ForeignKey("canonical_products.id", ondelete="CASCADE"), nullable=False, index=True)
    target_unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False) # Umbral de precio normalizado
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relación
    canonical_product = relationship("CanonicalProduct", back_populates="alerts")


class NotificationLog(Base):
    """
    Log de auditoría de mensajes enviados (WhatsApp, Webhook o Mock).
    """
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_alerts.id", ondelete="SET NULL"), nullable=True)
    recipient_phone: Mapped[str] = mapped_column(String(25), nullable=False)
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False) # 'mock', 'twilio_sandbox', 'meta_cloud'
    status: Mapped[str] = mapped_column(String(30), nullable=False) # 'sent', 'delivered', 'failed', 'simulated'
    dispatched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
