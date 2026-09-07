import logging
from typing import List, Optional
import numpy as np
from app.core.config import settings

logger = logging.getLogger("ofertis.vector_service")

# Singleton para el modelo de embeddings
_model_instance = None


def get_embedding_model():
    """
    Carga perezosa (lazy loading) del modelo multilingüe de SentenceTransformers.
    Genera vectores densos de 384 dimensiones optimizados para español.
    """
    global _model_instance
    if _model_instance is None:
        try:
            logger.info(f"Cargando modelo de embeddings: {settings.EMBEDDING_MODEL_NAME}...")
            from sentence_transformers import SentenceTransformer
            _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("Modelo de embeddings cargado exitosamente.")
        except Exception as e:
            logger.warning(f"No se pudo cargar SentenceTransformer en local ({e}). Usando fallback de hash pseudo-aleatorio determinista.")
            _model_instance = "FALLBACK"
    return _model_instance


class VectorService:
    """
    Servicio de inteligencia artificial para generación y comparación de embeddings vectoriales.
    """

    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """
        Transforma un texto o título de producto en un vector float de 384 dimensiones.
        """
        model = get_embedding_model()
        if model != "FALLBACK" and model is not None:
            try:
                embedding = model.encode(text, normalize_embeddings=True)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"Error generando embedding con SentenceTransformer: {e}")

        # Fallback determinista para pruebas si no hay torch disponible
        import hashlib
        seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(settings.EMBEDDING_DIMENSION)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calcula la similitud de coseno entre dos vectores normalizados (valor entre -1.0 y 1.0).
        """
        a = np.array(vec_a)
        b = np.array(vec_b)
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))
