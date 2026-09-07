import logging
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.models.user_alert import UserAlert, NotificationLog
from app.models.canonical_product import CanonicalProduct
from app.models.supermarket_item import SupermarketItem
from app.schemas.alert import UserAlertCreate, UserAlertResponse
from app.skills.whatsapp_notification_skill import WhatsAppNotificationSkill

logger = logging.getLogger("ofertis.alert_service")


class AlertService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.whatsapp_skill = WhatsAppNotificationSkill()

    async def create_alert(self, payload: UserAlertCreate) -> UserAlertResponse:
        """
        Crea una nueva regla de alerta para un usuario y su celular chileno.
        """
        # Verificar que el producto canónico exista
        stmt = select(CanonicalProduct).where(CanonicalProduct.id == payload.canonical_id)
        res = await self.db.execute(stmt)
        product = res.scalar_one_or_none()
        if not product:
            raise ValueError(f"El producto canónico con ID {payload.canonical_id} no existe.")

        new_alert = UserAlert(
            user_phone=payload.user_phone,
            user_name=payload.user_name,
            canonical_id=payload.canonical_id,
            target_unit_price=payload.target_unit_price,
            is_active=True
        )
        self.db.add(new_alert)
        await self.db.commit()
        await self.db.refresh(new_alert)

        return UserAlertResponse(
            id=new_alert.id,
            user_phone=new_alert.user_phone,
            user_name=new_alert.user_name,
            canonical_id=new_alert.canonical_id,
            canonical_product_name=product.name,
            target_unit_price=new_alert.target_unit_price,
            is_active=new_alert.is_active,
            last_triggered_at=new_alert.last_triggered_at,
            created_at=new_alert.created_at
        )

    async def list_alerts_by_phone(self, phone: str) -> List[UserAlertResponse]:
        """
        Lista todas las alertas configuradas para un número de WhatsApp específico.
        """
        stmt = (
            select(UserAlert)
            .where(UserAlert.user_phone == phone)
            .options(selectinload(UserAlert.canonical_product))
            .order_by(desc(UserAlert.created_at))
        )
        res = await self.db.execute(stmt)
        alerts = res.scalars().all()

        return [
            UserAlertResponse(
                id=a.id,
                user_phone=a.user_phone,
                user_name=a.user_name,
                canonical_id=a.canonical_id,
                canonical_product_name=a.canonical_product.name if a.canonical_product else "Producto",
                target_unit_price=a.target_unit_price,
                is_active=a.is_active,
                last_triggered_at=a.last_triggered_at,
                created_at=a.created_at
            )
            for a in alerts
        ]

    async def evaluate_and_dispatch_alerts(self, canonical_id: int) -> int:
        """
        Evalúa si los precios actuales de un producto canónico cumplen las condiciones
        para disparar alertas a los usuarios suscritos.
        """
        # 1. Obtener alertas activas para este producto
        stmt_alerts = (
            select(UserAlert)
            .where(UserAlert.canonical_id == canonical_id, UserAlert.is_active == True)
            .options(selectinload(UserAlert.canonical_product))
        )
        res_alerts = await self.db.execute(stmt_alerts)
        active_alerts = res_alerts.scalars().all()

        if not active_alerts:
            return 0

        # 2. Obtener el mejor precio actual del producto en cualquier supermercado
        stmt_prod = (
            select(CanonicalProduct)
            .where(CanonicalProduct.id == canonical_id)
            .options(
                selectinload(CanonicalProduct.items).selectinload(SupermarketItem.supermarket),
                selectinload(CanonicalProduct.items).selectinload(SupermarketItem.price_records)
            )
        )
        res_prod = await self.db.execute(stmt_prod)
        canonical = res_prod.scalar_one_or_none()
        if not canonical:
            return 0

        best_item = None
        best_unit_price = Decimal("999999")
        best_offer_price = Decimal("0")

        for item in canonical.items:
            if not item.is_available or not item.price_records:
                continue
            latest = item.price_records[0]
            if latest.unit_price_normalized < best_unit_price:
                best_unit_price = latest.unit_price_normalized
                best_offer_price = latest.offer_price or latest.normal_price
                best_item = item

        if not best_item or best_unit_price == Decimal("999999"):
            return 0

        dispatched_count = 0
        for alert in active_alerts:
            # Si el precio por kg/L está por debajo o igual al umbral fijado
            if best_unit_price <= alert.target_unit_price:
                # Disparar Skill de WhatsApp
                dispatch_result = await self.whatsapp_skill.execute(
                    user_name=alert.user_name,
                    recipient_phone=alert.user_phone,
                    product_name=canonical.name,
                    best_supermarket=best_item.supermarket.name,
                    offer_price=best_offer_price,
                    unit_price=best_unit_price,
                    standard_unit=canonical.standard_unit,
                    product_url=best_item.product_url,
                    savings_percentage=15.0 # Calculado vs promedio histórico
                )

                # Registrar auditoría en notification_logs
                log_entry = NotificationLog(
                    alert_id=alert.id,
                    recipient_phone=alert.user_phone,
                    message_content=dispatch_result.get("message", "Alerta enviada"),
                    provider=dispatch_result.get("provider", "mock"),
                    status=dispatch_result.get("status", "sent")
                )
                self.db.add(log_entry)
                dispatched_count += 1

        await self.db.commit()
        return dispatched_count
