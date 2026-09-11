import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.harvester_agent import HarvesterAgent
from app.agents.normalizer_agent import NormalizerAgent
from app.agents.entity_resolution_agent import EntityResolutionAgent
from app.agents.alert_monitor_agent import AlertMonitorAgent

logger = logging.getLogger("ofertis.agents.orchestrator")


class MultiAgentOrchestrator:
    """
    Orquestador Multi-Agente de Ofertis.
    Ejecuta el pipeline colaborativo entre agentes en bucle continuo o bajo demanda:
    1. HarvesterAgent: Mina y extrae catálogos crudos de Lider, Jumbo, Santa Isabel y Unimarc.
    2. NormalizerAgent: Estandariza pesos, volúmenes ($/kg, $/L) y taxonomías NCh 1424.
    3. EntityResolutionAgent: Agrupa SKUs mediante pgvector ($>0.85$ similitud semántica).
    4. AlertMonitorAgent: Evalúa umbrales y dispara alertas de WhatsApp a celulares chilenos.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.harvester = HarvesterAgent()
        self.normalizer = NormalizerAgent()
        self.resolver = EntityResolutionAgent(db)
        self.alert_monitor = AlertMonitorAgent(db)

    async def execute_full_cycle(self, limit_per_query: int = 4, target_queries: list = None) -> Dict[str, Any]:
        logger.info("=== INICIANDO CICLO MULTI-AGENTE OFERTIS CHILE ===")

        # 1. Loop de Minería (Harvester)
        harvest_result = await self.harvester.run_once(limit_per_query=limit_per_query, target_queries=target_queries)
        raw_items = harvest_result.get("data", {}).get("raw_items", [])
        logger.info(f"Harvester finalizado: {len(raw_items)} items recolectados.")

        # 2. Loop de Limpieza y Normalización (Normalizer)
        norm_result = await self.normalizer.run_once(raw_items=raw_items)
        normalized_items = norm_result.get("data", {}).get("normalized_items", [])
        logger.info(f"Normalizer finalizado: {len(normalized_items)} items normalizados.")

        # 3. Loop de Conocimiento y Deduplicación Semántica (Entity Resolution con pgvector)
        resolve_result = await self.resolver.run_once(normalized_items=normalized_items)
        affected_canonical_ids = resolve_result.get("data", {}).get("canonical_products_affected", [])
        logger.info(f"EntityResolution finalizado: {len(affected_canonical_ids)} productos canónicos actualizados.")

        # 4. Loop de Alertas y Notificaciones WhatsApp (Alert Monitor)
        alert_result = await self.alert_monitor.run_once(canonical_ids=affected_canonical_ids)
        alerts_sent = alert_result.get("data", {}).get("alerts_dispatched", 0)
        logger.info(f"AlertMonitor finalizado: {alerts_sent} alertas despachadas.")

        logger.info("=== CICLO MULTI-AGENTE COMPLETADO EXITOSAMENTE ===")

        return {
            "status": "completed",
            "stages": {
                "harvester": harvest_result,
                "normalizer": norm_result,
                "entity_resolution": resolve_result,
                "alert_monitor": alert_result
            },
            "summary": {
                "items_harvested": len(raw_items),
                "items_normalized": len(normalized_items),
                "canonical_products_affected": len(affected_canonical_ids),
                "whatsapp_alerts_sent": alerts_sent
            }
        }
