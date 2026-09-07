import logging
from typing import Any, Dict
from decimal import Decimal

try:
    from app.core.config import settings
except ImportError:
    class FallbackSettings:
        WHATSAPP_PROVIDER = "mock"
        TWILIO_ACCOUNT_SID = ""
        TWILIO_AUTH_TOKEN = ""
        TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
    settings = FallbackSettings()

from app.skills.base import BaseSkill

logger = logging.getLogger("ofertis.whatsapp")


class WhatsAppNotificationSkill(BaseSkill):
    """
    Skill para despachar alertas de ofertas a usuarios de WhatsApp en Chile (+56 9...).
    Soporta modo simulado ('mock') y modo 'twilio_sandbox' o 'meta_cloud'.
    """

    @property
    def name(self) -> str:
        return "WhatsAppNotificationSkill"

    @property
    def description(self) -> str:
        return "Despacha alertas enriquecidas de ofertas con formato WhatsApp (*negrita*, emojis, enlace y comparativa de ahorro)."

    def format_alert_message(
        self,
        user_name: str,
        product_name: str,
        best_supermarket: str,
        offer_price: Decimal,
        unit_price: Decimal,
        standard_unit: str,
        product_url: str,
        savings_percentage: float = 0.0
    ) -> str:
        """
        Formatea el mensaje con los estándares de diseño de WhatsApp para Chile.
        """
        saving_text = f" 🔥 *{savings_percentage:.0f}% de descuento detectado!*" if savings_percentage > 5 else ""
        return (
            f"🔔 *¡Alerta de Oferta Ofertis Chile!* 🇨🇱\n\n"
            f"Hola *{user_name}*, encontramos el mejor precio para tu producto vigilado:\n\n"
            f"🥩 *Producto:* {product_name}\n"
            f"🛒 *Supermercado:* *{best_supermarket}*\n"
            f"💵 *Precio Oferta:* *${offer_price:,.0f} CLP*\n"
            f"⚖️ *Precio por {standard_unit}:* *${unit_price:,.0f} CLP / {standard_unit}*{saving_text}\n\n"
            f"📲 *Ir a la tienda:* {product_url}\n\n"
            f"_Ofertis Bot - Comparador Inteligente de Canasta Básica_"
        )

    async def send_via_twilio(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Envía un mensaje de WhatsApp a través del cliente Twilio.
        """
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message_instance = client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                body=message,
                to=f"whatsapp:{to_phone}"
            )
            return {
                "status": "sent",
                "sid": message_instance.sid,
                "provider": "twilio_sandbox"
            }
        except Exception as e:
            logger.error(f"Error despachando WhatsApp vía Twilio a {to_phone}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "provider": "twilio_sandbox"
            }

    async def execute(
        self,
        user_name: str,
        recipient_phone: str,
        product_name: str,
        best_supermarket: str,
        offer_price: Decimal,
        unit_price: Decimal,
        standard_unit: str,
        product_url: str,
        savings_percentage: float = 0.0,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Ejecución del despacho de alerta.
        """
        message = self.format_alert_message(
            user_name=user_name,
            product_name=product_name,
            best_supermarket=best_supermarket,
            offer_price=offer_price,
            unit_price=unit_price,
            standard_unit=standard_unit,
            product_url=product_url,
            savings_percentage=savings_percentage
        )

        provider = settings.WHATSAPP_PROVIDER.lower()

        if provider == "twilio_sandbox" and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            result = await self.send_via_twilio(recipient_phone, message)
        else:
            # Modo Simulado / Mock para desarrollo local seguro sin costo
            logger.info(f"\n[WHATSAPP DISPATCHER (MOCK)] -> Enviar a {recipient_phone}:\n{message}\n")
            result = {
                "status": "simulated",
                "recipient_phone": recipient_phone,
                "message": message,
                "provider": "mock"
            }

        return result
