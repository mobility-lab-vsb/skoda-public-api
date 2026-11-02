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
    timers: list[Timer] | None = None


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
