from pydantic import Field

from .base_model import BaseModel

# The API types these values as "number". Whole numbers stay int, so existing
# consumers keep getting the same values; only fractional ones become float.
Number = int | float


class EngineRange(BaseModel):
    """Details of the vehicle's engine range."""

    engine_type: str | None = None
    current_soc_in_percent: Number | None = Field(None, alias="currentSoCInPercent")
    current_fuel_level_in_percent: Number | None = None
    remaining_range_in_km: Number | None = None


class FuelStatus(BaseModel):
    """Details of the vehicle's fuel status and driving range."""

    car_type: str | None = None
    ad_blue_range: Number | None = None
    total_range_in_km: Number | None = None
    primary_engine_range: EngineRange | None = None
    secondary_engine_range: EngineRange | None = None
    car_captured_timestamp: str | None = None
