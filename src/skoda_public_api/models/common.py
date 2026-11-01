from datetime import datetime
from typing import Optional, Union
from pydantic import Field

from .base_model import BaseModel
from .enums import ( 
    TemperatureUnit,
    VehicleErrorState
)


class TargetTemperature(BaseModel):
    """Target temperature settings for the vehicle."""
    value: float
    unit: TemperatureUnit 

class VehicleError(BaseModel):
    """Error information related to the vehicle."""
    # Unknown (future) error types are kept as plain strings instead of failing
    # validation of the whole response. left_to_right makes known values parse
    # as VehicleErrorState rather than matching the str branch.
    type: Union[VehicleErrorState, str] = Field(union_mode="left_to_right")
    description: Optional[str] = None
