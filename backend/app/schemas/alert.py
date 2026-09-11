from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
import re


class UserAlertCreate(BaseModel):
    user_phone: str = Field(..., description="Teléfono celular chileno con formato +569... o 9...")
    user_name: str = Field(default="Usuario", max_length=100)
    canonical_id: int = Field(..., gt=0, description="ID del producto canónico a monitorear")
    target_unit_price: Decimal = Field(..., gt=0, description="Precio máximo deseado por kg o L")

    @field_validator("user_phone")
    @classmethod
    def validate_chilean_phone(cls, v: str) -> str:
        # Limpiar espacios, guiones y caracteres no numéricos excepto '+'
        cleaned = re.sub(r"[^\d+]", "", v)
        if cleaned.startswith("+569") and len(cleaned) == 12:
            return cleaned
        elif cleaned.startswith("569") and len(cleaned) == 11:
            return f"+{cleaned}"
        elif cleaned.startswith("9") and len(cleaned) == 9:
            return f"+56{cleaned}"
        elif len(cleaned) == 8:
            return f"+569{cleaned}"
        raise ValueError("El número de teléfono debe ser un celular chileno válido (ej: +56912345678 o 912345678)")


class UserAlertResponse(BaseModel):
    id: int
    user_phone: str
    user_name: str
    canonical_id: int
    canonical_product_name: str
    target_unit_price: Decimal
    is_active: bool
    last_triggered_at: Optional[datetime] = None
    created_at: datetime
