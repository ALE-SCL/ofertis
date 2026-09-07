import asyncio
import logging
from typing import Any, Dict, List, Optional

try:
    from app.core.config import settings
except ImportError:
    class FallbackSettings:
        SCRAPER_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        SCRAPER_RATE_LIMIT_DELAY_SECONDS = 1.0
    settings = FallbackSettings()

from app.skills.base import BaseSkill

logger = logging.getLogger("ofertis.scraper")


class ScrapingSkill(BaseSkill):
    """
    Skill modular para minería de datos en retail chileno.
    Maneja sesiones HTTP asíncronas, rotación de headers y backoff exponencial.
    """

    @property
    def name(self) -> str:
        return "ScrapingSkill"

    @property
    def description(self) -> str:
        return "Cliente HTTP resiliente para extracción de catálogos en Jumbo, Santa Isabel, Unimarc y Lider."

    DEFAULT_HEADERS = {
        "User-Agent": settings.SCRAPER_USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-CL,es;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    async def fetch_json_safe(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una petición GET asíncrona con reintentos y backoff exponencial ante 429 o fallos temporales.
        """
        try:
            import httpx
        except ImportError:
            logger.error("Librería 'httpx' no instalada.")
            return None

        req_headers = {**self.DEFAULT_HEADERS, **(headers or {})}
        timeout = httpx.Timeout(15.0, connect=10.0)

        for attempt in range(1, max_retries + 1):
            try:
                # Respetar rate limiting antes de disparar la petición
                await asyncio.sleep(settings.SCRAPER_RATE_LIMIT_DELAY_SECONDS)

                async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                    response = await client.get(url, params=params, headers=req_headers)

                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code in (429, 503):
                        wait_time = attempt * 3.0
                        logger.warning(f"Rate limited (HTTP {response.status_code}) en {url}. Reintento {attempt} en {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.warning(f"Respuesta HTTP {response.status_code} desde {url}")
                        return None
            except Exception as e:
                logger.error(f"Error de conexión en intento {attempt}/{max_retries} para {url}: {e}")
                await asyncio.sleep(attempt * 2.0)

        return None

    async def execute(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
        data = await self.fetch_json_safe(url, params)
        return {"success": data is not None, "data": data}
