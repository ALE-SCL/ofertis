from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger("ofertis.agents")


class BaseAgent(ABC):
    """
    Clase abstracta base para los agentes autónomos de Ofertis.
    Maneja el ciclo de vida del bucle (Loop), métricas de ejecución y estado.
    """

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.state = "IDLE" # IDLE, RUNNING, SLEEPING, ERROR
        self.last_run_at: Optional[datetime] = None
        self.total_runs: int = 0
        self.error_count: int = 0

    @abstractmethod
    async def step(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Ejecuta una iteración o paso del bucle de trabajo del agente.
        """
        pass

    async def run_once(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Envuelve el paso de ejecución con captura de métricas y manejo de excepciones.
        """
        self.state = "RUNNING"
        self.last_run_at = datetime.now(timezone.utc)
        self.total_runs += 1

        try:
            result = await self.step(**kwargs)
            self.state = "IDLE"
            return {
                "agent": self.name,
                "role": self.role,
                "status": "success",
                "data": result
            }
        except Exception as e:
            self.state = "ERROR"
            self.error_count += 1
            logger.error(f"Error en bucle de {self.name}: {e}", exc_info=True)
            return {
                "agent": self.name,
                "role": self.role,
                "status": "error",
                "error": str(e)
            }
