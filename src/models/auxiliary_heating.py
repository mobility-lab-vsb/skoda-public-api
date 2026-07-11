from .base_model import BaseModel
from .common import TargetTemperature
from .enums import ( 
    AuxiliaryHeatingState,
    AuxiliaryHeatingStartMode,
)

class AuxiliaryHeating(BaseModel):
    """Auxiliary heating status."""
    state: AuxiliaryHeatingState
    start_mode: AuxiliaryHeatingStartMode
    duration_in_seconds: int
    target_temperature: TargetTemperature
    estimated_reach_of_target_temperature_at: str
    car_captured_timestamp: str
