from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import UserAlertCreate, UserAlertResponse

router = APIRouter(prefix="/alerts", tags=["WhatsApp Price Alerts"])


@router.post("", response_model=UserAlertResponse)
async def create_alert(
    payload: UserAlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea una alerta de WhatsApp para un celular chileno (+56 9...).
    Se disparará automáticamente cuando el precio/kg o precio/L caiga al umbral deseado.
    """
    service = AlertService(db)
    try:
        return await service.create_alert(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[UserAlertResponse])
async def list_user_alerts(
    phone: str = Query(..., description="Teléfono chileno del usuario"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista las alertas activas para un número de WhatsApp.
    """
    service = AlertService(db)
    return await service.list_alerts_by_phone(phone)


@router.post("/evaluate/{canonical_id}")
async def trigger_manual_evaluation(
    canonical_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Fuerza la evaluación del bucle de alertas para un producto canónico dado.
    """
    service = AlertService(db)
    dispatched = await service.evaluate_and_dispatch_alerts(canonical_id)
    return {
        "status": "success",
        "canonical_id": canonical_id,
        "notifications_dispatched": dispatched
    }
