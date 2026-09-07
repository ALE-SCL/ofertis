from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseSkill(ABC):
    """
    Clase abstracta base para todos los Skills del sistema Ofertis.
    Un Skill es una capacidad modular, reutilizable y testeable de forma aislada.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre identificador del Skill"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Descripción de la capacidad técnica del Skill"""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Ejecución asíncrona de la lógica del Skill"""
        pass
