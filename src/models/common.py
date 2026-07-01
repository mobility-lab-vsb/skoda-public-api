from datetime import datetime
from typing import Optional
from pydantic import Field

from .base_model import BaseModel
from .enums import ( 
    TemperatureUnit,
    VehicleErrorState
)


class TargetTemperature(BaseModel):
    """Target temperature settings for the vehicle."""
    value: float
    unit: TemperatureUnit 

class VehicleError(BaseModel):
    """Error information related to the vehicle."""
    type: VehicleErrorState
    description: str