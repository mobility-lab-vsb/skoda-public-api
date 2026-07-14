from typing import Optional, List

from .base_model import BaseModel
from .enums import (
    ChargingState,
    ChargeType,
    ChargeMode,
    ChargeCareModeState,
    AutoUnlockPlugState,
    MaxChargeCurrentAcState
)

class BatteryStatus(BaseModel):
    """Battery status information."""
    remaining_cruising_range_in_meters: Optional[int] = None
    state_of_charge_in_percent: Optional[int] = None

class ChargingStatus(BaseModel):
    """Charging status information."""
    charging_rate_in_kilometers_per_hour: Optional[float] = None
    charge_power_in_kw: Optional[float] = None
    remaining_time_to_fully_charged_in_minutes: Optional[int] = None
    fully_charged_at: Optional[str] = None
    state: Optional[ChargingState] = None
    charge_type: Optional[ChargeType] = None
    battery: Optional[BatteryStatus] = None

class ChargingSettings(BaseModel):
    """Information about charging settings."""
    target_state_of_charge_in_percent: Optional[int] = None
    battery_care_mode_target_value_in_percent: Optional[int] = None
    preferred_charge_mode: Optional[ChargeMode] = None
    available_charge_modes: Optional[List[ChargeMode]] = None
    charging_care_mode: Optional[ChargeCareModeState] = None
    auto_unlock_plug_when_charged: Optional[AutoUnlockPlugState] = None
    max_charge_current_ac: Optional[MaxChargeCurrentAcState] = None
    max_charge_current_ac_ampere: Optional[int] = None

class Charging(BaseModel):
    """Charging represents information about charging and battery settings."""
    is_vehicle_in_saved_location: Optional[bool] = None
    status: Optional[ChargingStatus] = None
    settings: Optional[ChargingSettings] = None
    car_captured_timestamp: Optional[str] = None