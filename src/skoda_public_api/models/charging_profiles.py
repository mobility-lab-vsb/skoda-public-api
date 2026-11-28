from typing import Any

from pydantic import Field, field_validator

from .base_model import BaseModel


class Timer(BaseModel):
    """Details of the profiles timer."""

    id: int
    enabled: bool
    time: str | None = None
    type: str
    one_off_day: str | None = None
    recurring_on: list[str] | None = None


class ChargingTime(BaseModel):
    """Details of the profiles' charging time."""

    id: int
    enabled: bool
    start_time: str
    end_time: str


class MinBatteryStateOfCharge(BaseModel):
    """Details of the minimum battery state of charge."""

    enabled: bool | None = None
    minimum_battery_state_of_charge_in_percent: int | None = None


class ChargingProfileSettings(BaseModel):
    """Details of the charging profile settings."""

    max_charging_current: str | None = None
    min_battery_state_of_charge: MinBatteryStateOfCharge | None = None
    target_state_of_charge_in_percent: int | None = None
    auto_unlock_plug_when_charged: str | None = None


class ChargingProfile(BaseModel):
    """Details of the vehicle's charging profile."""

    id: int
    name: str
    settings: ChargingProfileSettings
    preferred_charging_times: list[ChargingTime]
    # Required by the API when updating a profile, so it is never None.
    timers: list[Timer] = Field(default_factory=list)

    @field_validator("timers", mode="before")
    @classmethod
    def _timers_none_as_empty(cls, value: Any) -> Any:
        """Treat a null timers list in a response as no timers."""
        return [] if value is None else value


class CurrentVehiclePositionProfile(BaseModel):
    """Returns information about actual profile, where vehicle is located."""

    id: int
    name: str
    target_state_of_charge_in_percent: int | None = None
    next_charging_time: str | None = None


class ChargingProfiles(BaseModel):
    """Details of the vehicle's charging profiles."""

    profiles: list[ChargingProfile]
    current_vehicle_position_profile: CurrentVehiclePositionProfile | None = None
    car_captured_timestamp: str | None = None
