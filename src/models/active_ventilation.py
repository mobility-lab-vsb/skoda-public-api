from .base_model import BaseModel
from .common import TargetTemperature
from .enums import ( 
    VentilationState
)

class ActiveVentilation(BaseModel):
    """Active ventilation status."""
    state: VentilationState
    duration_in_seconds: int
    car_captured_timestamp: str
