from typing import Optional

from .base_model import BaseModel
from .common import TargetTemperature
from .enums import OnOffState, AirConditioningState


class WindowHeating(BaseModel):
    """State of the electric window heating."""
    enabled: Optional[bool] = None
    front: Optional[OnOffState] = None
    rear: Optional[OnOffState] = None

class AirConditioning(BaseModel):
    """Information about the vehicle's air conditioning."""
    state: AirConditioningState
    target_temperature: Optional[TargetTemperature] = None
    estimated_reach_of_target_temperature_at: Optional[str] = None
    air_conditioning_without_external_power: Optional[bool] = None
    air_conditioning_at_unlock: Optional[bool] = None
    window_heating: Optional[WindowHeating] = None
    car_captured_timestamp: Optional[str] = None