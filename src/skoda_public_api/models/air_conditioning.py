from .base_model import BaseModel
from .common import TargetTemperature
from .enums import AirConditioningState, OnOffState


class WindowHeating(BaseModel):
    """State of the electric window heating."""

    enabled: bool | None = None
    front: OnOffState | None = None
    rear: OnOffState | None = None


class AirConditioning(BaseModel):
    """Information about the vehicle's air conditioning."""

    state: AirConditioningState
    target_temperature: TargetTemperature | None = None
    estimated_reach_of_target_temperature_at: str | None = None
    air_conditioning_without_external_power: bool | None = None
    air_conditioning_at_unlock: bool | None = None
    window_heating: WindowHeating | None = None
    car_captured_timestamp: str | None = None
