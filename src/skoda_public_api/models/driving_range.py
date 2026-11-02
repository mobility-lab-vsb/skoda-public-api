from typing import Optional, Union

from pydantic import Field

from .base_model import BaseModel

# The API types these values as "number". Whole numbers stay int, so existing
# consumers keep getting the same values; only fractional ones become float.
Number = Union[int, float]


class EngineRange(BaseModel):
    """Details of the vehicle's engine range."""
    engine_type: Optional[str] = None
    current_soc_in_percent: Optional[Number] = Field(None, alias="currentSoCInPercent")
    current_fuel_level_in_percent: Optional[Number] = None
    remaining_range_in_km: Optional[Number] = None


class FuelStatus(BaseModel):
    """Details of the vehicle's fuel status and driving range."""
    car_type: Optional[str] = None
    ad_blue_range: Optional[Number] = None
    total_range_in_km: Optional[Number] = None
    primary_engine_range: Optional[EngineRange] = None
    secondary_engine_range: Optional[EngineRange] = None
    car_captured_timestamp: Optional[str] = None