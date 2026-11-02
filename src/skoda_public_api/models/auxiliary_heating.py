from .base_model import BaseModel
from .common import TargetTemperature
from .enums import (
    AuxiliaryHeatingStartMode,
    AuxiliaryHeatingState,
)


class AuxiliaryHeating(BaseModel):
    """Auxiliary heating status."""

    state: AuxiliaryHeatingState
    start_mode: AuxiliaryHeatingStartMode | None = None
    duration_in_seconds: int | None = None
    target_temperature: TargetTemperature | None = None
    estimated_reach_of_target_temperature_at: str | None = None
    car_captured_timestamp: str | None = None
