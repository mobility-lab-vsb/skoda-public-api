from typing import Optional
from .base_model import BaseModel
from .common import TargetTemperature
from .enums import ( 
    VentilationState
)

class ActiveVentilation(BaseModel):
    """Active ventilation status."""
    state: VentilationState
    duration_in_seconds: Optional[int] = None
    car_captured_timestamp:  Optional[str] = None
