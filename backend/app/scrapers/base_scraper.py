from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class RawScrapedProduct:
    """
    Estructura de datos cruda extraída desde la API o catálogo web del supermercado.
    """
    supermarket_slug: str # 'lider', 'jumbo', 'santaisabel', 'unimarc'
    sku: str
    store_title: str
    brand_raw: Optional[str]
    normal_price: Decimal
    offer_price: Optional[Decimal]
    product_url: str
    image_url: Optional[str]
    category_hint: str # 'carne_vacuno', 'leche', 'arroz', 'fideos'


class BaseScraperAdapter(ABC):
    """
    Contrato base para adaptadores de minería de datos por supermercado chileno.
    """

    @property
    @abstractmethod
    def supermarket_slug(self) -> str:
        pass

    @property
    @abstractmethod
    def supermarket_name(self) -> str:
        pass

    @abstractmethod
    async def search_category(
        self,
        category: str,
        query: str,
        limit: int = 20
    ) -> List[RawScrapedProduct]:
        """
        Ejecuta la extracción de productos para una categoría y término específico.
        """
        pass
