from pydantic import Field

from .base_model import BaseModel


class ConfigurationTargetTemperature(BaseModel):
    value: float = Field(..., alias="value")
    unit: str = Field("CELSIUS", alias="unit")


class StartAirConditioningConfiguration(BaseModel):
    """Configuration for starting air conditioning."""

    target_temperature: ConfigurationTargetTemperature | None = Field(
        None, alias="targetTemperature"
    )
    heater_source: str | None = Field(None, alias="heaterSource")
    air_conditioning_without_external_power: bool | None = Field(
        True, alias="airConditioningWithoutExternalPower"
    )


class StartAuxiliaryHeatingConfiguration(BaseModel):
    """Configuration for starting auxiliary heating."""

    spin: str = Field(..., alias="spin")
    duration_in_seconds: int | None = Field(120, alias="durationInSeconds")
    start_mode: str | None = Field("HEATING", alias="startMode")
    target_temperature: ConfigurationTargetTemperature | None = Field(
        None, alias="targetTemperature"
    )


class ChargingLimitConfiguration(BaseModel):
    """Configuration for setting the charging limit."""

    target_state_of_charge_in_percent: int = Field(
        ..., alias="targetStateOfChargeInPercent"
    )
