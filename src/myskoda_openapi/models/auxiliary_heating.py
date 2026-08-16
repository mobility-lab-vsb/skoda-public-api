from typing import Optional
from .base_model import BaseModel
from .common import TargetTemperature
from .enums import ( 
    AuxiliaryHeatingState,
    AuxiliaryHeatingStartMode,
)


class AuxiliaryHeating(BaseModel):
    """Auxiliary heating status."""
    state: AuxiliaryHeatingState
    start_mode: Optional[AuxiliaryHeatingStartMode] = None
    duration_in_seconds: Optional[int] = None
    target_temperature:  Optional[TargetTemperature] = None
    estimated_reach_of_target_temperature_at: Optional[str] = None
    car_captured_timestamp: Optional[str] = None
