from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.radar_service import RadarService

router = APIRouter(prefix="/radar", tags=["Radar Alternativo & Canales de Ahorro"])


@router.get("/opportunities")
async def get_radar_opportunities(
    category: Optional[str] = Query(None, description="Filtro opcional: 'carnes', 'despensa', 'frutas_verduras', 'lacteos_huevos'"),
    store: Optional[str] = Query(None, description="Filtro opcional por slug de tienda: 'alvi', 'central_mayorista', 'dona_carne', 'el_carnicero', 'comercial_castro', 'lo_valledor', 'acuenta', etc."),
    q: Optional[str] = Query(None, description="Búsqueda por texto (corte, producto o tienda)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna las oportunidades de ahorro comprobadas en canales alternativos
    (Doña Carne, El Carnicero, Alvi, Central Mayorista, SuperBodega aCuenta, Lo Valledor, etc.)
    persistidas en PostgreSQL con cálculo dinámico del spread frente al retail tradicional.
    """
    return await RadarService.get_opportunities_async(db=db, category=category, q=q, store=store)


@router.get("/stores")
async def get_alternative_stores(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna la lista de tiendas y mercados alternativos y mayoristas monitoreados.
    """
    return await RadarService.get_alternative_stores_async(db=db)


@router.get("/kpis")
async def get_radar_kpis(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna los indicadores clave de ahorro (Spread promedio, ahorro máximo y conteos) desde la BD.
    """
    return await RadarService.get_kpis_async(db=db)


@router.get("/items/{sku}/history")
async def get_radar_item_price_history(
    sku: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna el historial de precios y ahorros para un SKU de canal alternativo o mayorista.
    """
    return await RadarService.get_item_price_history_async(db=db, item_sku=sku)

