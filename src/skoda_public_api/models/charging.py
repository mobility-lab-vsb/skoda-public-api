from .base_model import BaseModel
from .enums import (
    AutoUnlockPlugState,
    ChargeCareModeState,
    ChargeMode,
    ChargeType,
    ChargingState,
    LockState,
    MaxChargeCurrentAcState,
    PlugConnectionState,
)


class BatteryStatus(BaseModel):
    """Battery status information."""

    remaining_cruising_range_in_meters: int | None = None
    state_of_charge_in_percent: int | None = None


class ChargingStatus(BaseModel):
    """Charging status information."""

    charging_rate_in_kilometers_per_hour: float | None = None
    charge_power_in_kw: float | None = None
    remaining_time_to_fully_charged_in_minutes: int | None = None
    fully_charged_at: str | None = None
    state: ChargingState | None = None
    charge_type: ChargeType | None = None
    plug_connection_state: PlugConnectionState | None = None
    plug_lock_state: LockState | None = None
    battery: BatteryStatus | None = None


class ChargingSettings(BaseModel):
    """Information about charging settings."""

    target_state_of_charge_in_percent: int | None = None
    battery_care_mode_target_value_in_percent: int | None = None
    preferred_charge_mode: ChargeMode | None = None
    available_charge_modes: list[ChargeMode] | None = None
    charging_care_mode: ChargeCareModeState | None = None
    auto_unlock_plug_when_charged: AutoUnlockPlugState | None = None
    max_charge_current_ac: MaxChargeCurrentAcState | None = None
    max_charge_current_ac_ampere: int | None = None


class Charging(BaseModel):
    """Charging represents information about charging and battery settings."""

    is_vehicle_in_saved_location: bool
    status: ChargingStatus | None = None
    settings: ChargingSettings | None = None
    car_captured_timestamp: str | None = None
