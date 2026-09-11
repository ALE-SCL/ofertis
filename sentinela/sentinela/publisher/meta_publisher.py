"""
Conector y Publicador Automatizado en Redes Sociales (Meta Graph API).
Publica carruseles visuales de 5 diapositivas en:
1. Página de Facebook (Álbum / Multi-Photo Feed Post).
2. Feed de Instagram (Carrusel Nativo de Imágenes).
"""

import os
import json
import time
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

logger = logging.getLogger("sentinela.meta_publisher")

GRAPH_API_VERSION = "v20.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class MetaSocialPublisher:
    def __init__(
        self,
        access_token: Optional[str] = None,
        facebook_page_id: Optional[str] = None,
        instagram_account_id: Optional[str] = None,
        public_base_url: Optional[str] = None,
    ):
        """
        Inicializa las credenciales de publicación.
        Se leen prioritariamente de variables de entorno si no se especifican.
        """
        self.access_token = access_token or os.getenv("META_ACCESS_TOKEN") or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        self.facebook_page_id = facebook_page_id or os.getenv("FACEBOOK_PAGE_ID")
        self.instagram_account_id = instagram_account_id or os.getenv("INSTAGRAM_ACCOUNT_ID") or os.getenv("INSTAGRAM_USER_ID")

        # URL base pública desde la cual Meta puede descargar las imágenes
        # Ej: https://ofertis-backend.onrender.com o https://ofertis.cl
        self.public_base_url = (public_base_url or os.getenv("PUBLIC_BASE_URL") or "https://ofertis-backend.onrender.com").rstrip("/")

    def _http_post(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una petición POST JSON / Form URL-Encoded a la Graph API de Meta."""
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded_data, method="POST")
        req.add_header("User-Agent", "Ofertis-Sentinela-Publisher/1.0")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8") if e.fp else ""
            logger.error(f"Meta Graph API HTTP Error {e.code}: {err_body}")
            try:
                return json.loads(err_body)
            except Exception:
                return {"error": {"message": f"HTTP {e.code}: {e.reason}", "code": e.code}}
        except Exception as e:
            logger.error(f"Error de conexión con Meta Graph API: {e}")
            return {"error": {"message": str(e)}}

    def _http_get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una petición GET a la Graph API de Meta."""
        query_str = urllib.parse.urlencode(params)
        full_url = f"{url}?{query_str}" if query_str else url
        req = urllib.request.Request(full_url, method="GET")
        req.add_header("User-Agent", "Ofertis-Sentinela-Publisher/1.0")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except Exception as e:
            logger.error(f"Error GET Meta Graph API: {e}")
            return {"error": {"message": str(e)}}

    def is_configured_for_facebook(self) -> bool:
        return bool(self.access_token and self.facebook_page_id)

    def is_configured_for_instagram(self) -> bool:
        return bool(self.access_token and self.instagram_account_id)

    def publish_carousel_to_facebook(
        self,
        slide_urls: List[str],
        caption: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Publica un post multi-foto en la Página de Facebook.
        Subiendo cada diapositiva como foto oculta y luego publicando un feed post con attached_media.
        """
        if dry_run or not self.is_configured_for_facebook():
            logger.info("ℹ️ [DRY-RUN / NO-CONFIG] Facebook Post simulado:")
            logger.info(f"   • Page ID: {self.facebook_page_id or '(No configurado)'}")
            logger.info(f"   • Slides a subir: {len(slide_urls)}")
            logger.info(f"   • Extracto caption: {caption[:120]}...")
            return {
                "success": True,
                "platform": "facebook",
                "mode": "dry_run" if dry_run else "unconfigured",
                "message": "Publicación de Facebook simulada con éxito. Agrega META_ACCESS_TOKEN y FACEBOOK_PAGE_ID para publicar en vivo.",
                "slides_count": len(slide_urls)
            }

        logger.info(f"🚀 Publicando carrusel en Facebook Page ID: {self.facebook_page_id} ({len(slide_urls)} slides)...")

        # 1. Subir cada imagen como foto no publicada
        photo_ids = []
        for idx, url in enumerate(slide_urls):
            upload_endpoint = f"{GRAPH_API_BASE}/{self.facebook_page_id}/photos"
            payload = {
                "url": url,
                "published": "false",
                "access_token": self.access_token
            }
            res = self._http_post(upload_endpoint, payload)
            photo_id = res.get("id")
            if photo_id:
                photo_ids.append(photo_id)
                logger.info(f"   ✓ Foto {idx+1}/{len(slide_urls)} subida a Facebook (ID: {photo_id})")
            else:
                logger.warning(f"   ⚠️ Error subiendo foto {idx+1}: {res}")

        if not photo_ids:
            return {"success": False, "platform": "facebook", "error": "No se pudo subir ninguna foto a Facebook"}

        # 2. Publicar el post multi-foto en el feed de la página
        feed_endpoint = f"{GRAPH_API_BASE}/{self.facebook_page_id}/feed"
        attached_media = [{"media_fbid": pid} for pid in photo_ids]

        feed_payload = {
            "message": caption,
            "attached_media": json.dumps(attached_media),
            "access_token": self.access_token
        }

        res = self._http_post(feed_endpoint, feed_payload)
        post_id = res.get("id")

        if post_id:
            logger.info(f"✅ Post multi-foto publicado exitosamente en Facebook: ID {post_id}")
            return {
                "success": True,
                "platform": "facebook",
                "post_id": post_id,
                "url": f"https://www.facebook.com/{post_id}"
            }
        else:
            logger.error(f"❌ Error al crear post en Facebook: {res}")
            return {"success": False, "platform": "facebook", "error": res}

    def publish_carousel_to_instagram(
        self,
        slide_urls: List[str],
        caption: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Publica un carrusel de imágenes nativo en el feed de Instagram.
        Crea contenedores de items, contenedor de carrusel, y ejecuta media_publish.
        """
        if dry_run or not self.is_configured_for_instagram():
            logger.info("ℹ️ [DRY-RUN / NO-CONFIG] Instagram Carousel simulado:")
            logger.info(f"   • IG Account ID: {self.instagram_account_id or '(No configurado)'}")
            logger.info(f"   • Slides a subir: {len(slide_urls)}")
            logger.info(f"   • Extracto caption: {caption[:120]}...")
            return {
                "success": True,
                "platform": "instagram",
                "mode": "dry_run" if dry_run else "unconfigured",
                "message": "Publicación de Instagram simulada con éxito. Agrega META_ACCESS_TOKEN e INSTAGRAM_ACCOUNT_ID para publicar en vivo.",
                "slides_count": len(slide_urls)
            }

        logger.info(f"🚀 Publicando carrusel en Instagram Account ID: {self.instagram_account_id} ({len(slide_urls)} slides)...")

        # 1. Crear contenedor individual para cada diapositiva
        item_container_ids = []
        for idx, url in enumerate(slide_urls):
            endpoint = f"{GRAPH_API_BASE}/{self.instagram_account_id}/media"
            payload = {
                "image_url": url,
                "is_carousel_item": "true",
                "access_token": self.access_token
            }
            res = self._http_post(endpoint, payload)
            cid = res.get("id")
            if cid:
                item_container_ids.append(cid)
                logger.info(f"   ✓ Item {idx+1}/{len(slide_urls)} listo en Instagram (Container: {cid})")
            else:
                logger.warning(f"   ⚠️ Error creando contenedor para slide {idx+1}: {res}")

        if len(item_container_ids) < 2:
            return {
                "success": False,
                "platform": "instagram",
                "error": f"Instagram exige mínimo 2 diapositivas para un carrusel (se obtuvieron {len(item_container_ids)})"
            }

        # 2. Crear contenedor padre de carrusel
        parent_endpoint = f"{GRAPH_API_BASE}/{self.instagram_account_id}/media"
        parent_payload = {
            "media_type": "CAROUSEL",
            "children": json.dumps(item_container_ids),
            "caption": caption,
            "access_token": self.access_token
        }

        res = self._http_post(parent_endpoint, parent_payload)
        carousel_container_id = res.get("id")

        if not carousel_container_id:
            logger.error(f"❌ Error creando contenedor padre de carrusel en Instagram: {res}")
            return {"success": False, "platform": "instagram", "error": res}

        logger.info(f"   ✓ Contenedor carrusel creado: {carousel_container_id}. Esperando procesamiento...")
        time.sleep(3)

        # 3. Publicar el carrusel
        publish_endpoint = f"{GRAPH_API_BASE}/{self.instagram_account_id}/media_publish"
        publish_payload = {
            "creation_id": carousel_container_id,
            "access_token": self.access_token
        }

        pub_res = self._http_post(publish_endpoint, publish_payload)
        media_id = pub_res.get("id")

        if media_id:
            logger.info(f"✅ Carrusel de Instagram publicado exitosamente: Media ID {media_id}")
            return {
                "success": True,
                "platform": "instagram",
                "media_id": media_id
            }
        else:
            logger.error(f"❌ Error al publicar carrusel en Instagram: {pub_res}")
            return {"success": False, "platform": "instagram", "error": pub_res}

    def publish_carousel(
        self,
        article_id: str,
        manifest: Dict[str, Any],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Coordina la publicación completa del carrusel tanto en Facebook como en Instagram
        usando las URLs públicas del backend de Ofertis.
        """
        slide_filenames = manifest.get("slide_filenames", ["slide_1.png", "slide_2.png", "slide_3.png", "slide_4.png", "slide_5.png"])
        caption = manifest.get("caption", "")

        # Construir las URLs públicas accesibles por Meta
        # Formato: https://ofertis-backend.onrender.com/static/carousels/{article_id}/slide_1.png
        slide_urls = [
            f"{self.public_base_url}/static/carousels/{article_id}/{fname}"
            for fname in slide_filenames
        ]

        logger.info(f"📢 Despachando carrusel para artículo: {article_id}")
        logger.info(f"🌐 URLs públicas: {slide_urls[0]} ... ({len(slide_urls)} slides)")

        fb_result = self.publish_carousel_to_facebook(slide_urls, caption, dry_run=dry_run)
        ig_result = self.publish_carousel_to_instagram(slide_urls, caption, dry_run=dry_run)

        return {
            "article_id": article_id,
            "timestamp": time.time(),
            "facebook": fb_result,
            "instagram": ig_result,
            "public_slide_urls": slide_urls
        }
