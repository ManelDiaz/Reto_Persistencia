from pydantic import BaseModel, Field, validator
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)

class Turbina(BaseModel):
    timestamp: datetime
    lv_active_power_kw: float = Field(ge=0, le=2000)
    wind_speed_ms: float = Field(ge=0, le=30)
    theoretical_power_curve_kwh: float = Field(ge=0, le=2000)    
    wind_direction_deg: float = Field(ge=0, le=360)
    
    @validator("wind_speed_ms")
    def validar_velocidad_viento(cls, v):
        if v < 0 or v > 30:
            logger.error("La velocidad del viento debe estar entre 0 y 30 m/s")
        return v