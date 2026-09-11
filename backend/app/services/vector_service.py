import logging
import math
from typing import List, Optional
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
        if not settings.USE_LOCAL_SENTENCE_TRANSFORMER:
            logger.info("Modo de embeddings ultraligero activo (optimizado para cloud/Render con 0 MB de sobrecarga).")
            _model_instance = "FALLBACK"
            return _model_instance
        try:
            logger.info(f"Cargando modelo de embeddings pesado: {settings.EMBEDDING_MODEL_NAME}...")
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

        # Fallback determinista semántico basado en Bag-of-Subwords & N-grams (hashing trick)
        # Permite correlación semántica real sin requerir modelos pesados en RAM
        import hashlib
        import math
        import re

        dim = settings.EMBEDDING_DIMENSION
        cleaned = re.sub(r"[^\w\s]", " ", text.lower()).strip()
        words = [w for w in cleaned.split() if w]
        vec = [0.0] * dim

        tokens = []
        for w in words:
            tokens.append((w, 2.5))
        for i in range(len(words) - 1):
            tokens.append((f"{words[i]}_{words[i+1]}", 1.8))
        for w in words:
            pad_w = f"<{w}>"
            for i in range(len(pad_w) - 2):
                tokens.append((pad_w[i:i+3], 0.8))

        for token, weight in tokens:
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % dim
            sign = 1.0 if (h >> 15) & 1 else -1.0
            vec[idx] += sign * weight

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calcula la similitud de coseno entre dos vectores normalizados (valor entre -1.0 y 1.0).
        """
        try:
            import numpy as np
            a = np.array(vec_a)
            b = np.array(vec_b)
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(dot_product / (norm_a * norm_b))
        except ImportError:
            dot_product = sum(x * y for x, y in zip(vec_a, vec_b))
            norm_a = math.sqrt(sum(x * x for x in vec_a))
            norm_b = math.sqrt(sum(y * y for y in vec_b))
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(dot_product / (norm_a * norm_b))
