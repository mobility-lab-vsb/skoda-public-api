from typing import Optional

from .base_model import BaseModel


class EngineRange(BaseModel):
    """Details of the vehicle's engine range."""
    engine_type: Optional[str] = None
    current_soc_in_percent: Optional[int] = None
    current_fuel_level_in_percent: Optional[int] = None
    remaining_range_in_km: Optional[int] = None


class FuelStatus(BaseModel):
    """Details of the vehicle's fuel status and driving range."""
    car_type: Optional[str] = None
    ad_blue_range: Optional[int] = None
    total_range_in_km: Optional[int] = None
    primary_engine_range: Optional[EngineRange] = None
    secondary_engine_range: Optional[EngineRange] = None
    car_captured_timestamp: Optional[str] = None