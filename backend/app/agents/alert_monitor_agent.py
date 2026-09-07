import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.base_agent import BaseAgent
from app.services.alert_service import AlertService

logger = logging.getLogger("ofertis.agents.alert_monitor")


class AlertMonitorAgent(BaseAgent):
    """
    Agente de Monitoreo de Alertas (Trigger Loop).
    Inspecciona productos con precios actualizados y despacha notificaciones WhatsApp.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(name="AlertMonitorAgent", role="WhatsApp Price Alert Dispatcher")
        self.alert_service = AlertService(db)

    async def step(self, canonical_ids: List[int], **kwargs: Any) -> Dict[str, Any]:
        """
        Evalúa las alertas para una lista de productos canónicos que tuvieron cambios de precio.
        """
        total_alerts_dispatched = 0

        for cid in canonical_ids:
            dispatched = await self.alert_service.evaluate_and_dispatch_alerts(cid)
            total_alerts_dispatched += dispatched

        return {
            "products_evaluated": len(canonical_ids),
            "alerts_dispatched": total_alerts_dispatched
        }
