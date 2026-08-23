from typing import List, Optional

from .base_model import BaseModel

class Timer(BaseModel):
    """Details of the profiles timer."""
    id: int
    enabled: bool
    time: Optional[str] = None
    type: str
    one_off_day: Optional[str] = None
    recurring_on: Optional[List[str]] = None

class ChargingTime(BaseModel):
    """Details of the profiles' charging time."""
    id: int
    enabled: bool
    start_time: str
    end_time: str

class MinBatteryStateOfCharge(BaseModel):
    """Details of the minimum battery state of charge."""
    enabled: Optional[bool] = None
    minimum_battery_state_of_charge_in_percent: Optional[int] = None
  
class ChargingProfileSettings(BaseModel):
    """Details of the charging profile settings."""
    max_charging_current: Optional[str] = None
    min_battery_state_of_charge: Optional[MinBatteryStateOfCharge] = None
    target_state_of_charge_in_percent: Optional[int] = None
    auto_unlock_plug_when_charged: Optional[str] = None

class ChargingProfile(BaseModel):
    """Details of the vehicle's charging profile."""
    id: int
    name: str
    settings: ChargingProfileSettings
    preferred_charging_times: List[ChargingTime]
    timers: List[Timer]


class ChargingProfiles(BaseModel):
    """Details of the vehicle's charging profiles."""
    profiles: List[ChargingProfile]
    current_vehicle_position_profile: Optional[ChargingProfile] = None
    car_captured_timestamp: Optional[str] = None