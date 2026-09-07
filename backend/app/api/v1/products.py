from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import (
    ProductSearchResult,
    CanonicalProductDetail,
)

router = APIRouter(prefix="/products", tags=["Products & Price Comparison"])


@router.get("/categories")
async def get_categories():
    """
    Retorna las categorías de canasta básica monitoreadas.
    """
    return [
        {"slug": "todos", "name": "Todos los Productos", "icon": "LayoutGrid"},
        {"slug": "carne_vacuno", "name": "Carnes de Vacuno (NCh 1424)", "icon": "Beef"},
        {"slug": "carne_cerdo", "name": "Carnes de Cerdo", "icon": "Ham"},
        {"slug": "carne_pollo", "name": "Pollo y Pavo", "icon": "Drumstick"},
        {"slug": "leche", "name": "Leches y Lácteos", "icon": "Milk"},
        {"slug": "arroz", "name": "Arroz", "icon": "Wheat"},
        {"slug": "fideos", "name": "Fideos y Pastas", "icon": "Utensils"},
    ]


@router.get("/search", response_model=List[ProductSearchResult])
async def search_products(
    q: str = Query(..., min_length=2, description="Texto de búsqueda semántica (ej: 'lomo liso', 'posta', 'arroz grado 1', 'leche descremada')"),
    category: Optional[str] = Query(None, description="Filtro opcional por categoría"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Búsqueda semántica vectorial de productos de primera necesidad.
    Usa pgvector para encontrar equivalencias sin importar cómo lo nombre cada supermercado.
    """
    service = ProductService(db)
    return await service.search_products(query=q, category=category, limit=limit)


@router.get("/{canonical_id}", response_model=CanonicalProductDetail)
async def get_product_detail(
    canonical_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la ficha comparativa del producto entre Jumbo, Santa Isabel, Unimarc y Lider,
    calculando la mejor opción y precio normalizado por kg o L.
    """
    service = ProductService(db)
    detail = await service.get_product_detail(canonical_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return detail


@router.get("/{canonical_id}/history")
async def get_product_price_history(
    canonical_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el historial cronológico de precios para graficar la evolución en el tiempo.
    """
    service = ProductService(db)
    return await service.get_price_history(canonical_id)
