from typing import Optional
from pydantic import Field
from .base_model import BaseModel

class ConfigurationTargetTemperature(BaseModel):
    value: float = Field(..., alias="value")
    unit: str = Field("CELSIUS", alias="unit")


class StartAirConditioningConfiguration(BaseModel):
    """Configuration for starting air conditioning."""
    target_temperature: Optional[ConfigurationTargetTemperature] = Field(None, alias="targetTemperature")
    heater_source: Optional[str] = Field(None, alias="heaterSource")
    air_conditioning_without_external_power: Optional[bool] = Field(
        True, alias="airConditioningWithoutExternalPower"
    )

class StartAuxiliaryHeatingConfiguration(BaseModel):
    """Configuration for starting auxiliary heating."""
    spin: str = Field(..., alias="spin")
    duration_in_seconds: Optional[int] = Field(120, alias="durationInSeconds")
    start_mode: Optional[str] = Field("HEATING", alias="startMode")
    target_temperature: Optional[ConfigurationTargetTemperature] = Field(None, alias="targetTemperature")