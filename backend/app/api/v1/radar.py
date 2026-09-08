from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query
from app.services.radar_service import RadarService

router = APIRouter(prefix="/radar", tags=["Radar Alternativo & Canales de Ahorro"])


@router.get("/opportunities")
async def get_radar_opportunities(
    category: Optional[str] = Query(None, description="Filtro opcional: 'carnes', 'despensa', 'frutas_verduras', 'lacteos_huevos'"),
    q: Optional[str] = Query(None, description="Búsqueda por texto (corte, producto o tienda)")
):
    """
    Retorna las oportunidades de ahorro comprobadas en canales alternativos
    (El Carnicero, SuperBodega aCuenta, Mercado Lo Valledor) con cálculo del spread
    frente a los precios del retail tradicional (Jumbo, Santa Isabel, Unimarc, Lider).
    """
    return RadarService.get_opportunities(category=category, q=q)


@router.get("/stores")
async def get_alternative_stores():
    """
    Retorna la lista de tiendas y mercados alternativos monitoreados.
    """
    return RadarService.get_alternative_stores()


@router.get("/kpis")
async def get_radar_kpis():
    """
    Retorna los indicadores clave de ahorro (Spread promedio, ahorro máximo y conteos).
    """
    return RadarService.get_kpis()
