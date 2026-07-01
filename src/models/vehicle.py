from datetime import datetime
from typing import List, Optional
from pydantic import Field

from .base_model import BaseModel
from .enums import (
    TemperatureUnit
)
from .vehicle_status import VehicleStatus
from .common import VehicleError

class Odometer(BaseModel):
    """Odometer of the vehicle."""
    mileage_in_km: int
    car_captured_timestamp: str  # Assuming the unit is always kilometers, adjust if needed.

class VehicleObject(BaseModel):
    """Pack whole vehicle object into one object for the vehicle."""
    name: str
    vin: str
    license_plate: str
    render_url: Optional[str] = None
    odometer: Optional[Odometer] = None
    status: Optional[VehicleStatus] = None
    #TODO: Add rest of the vehicle attributes like air_conditioning, driving_range, etc.

class VehicleResponse(BaseModel):
    """Response object for vehicle data."""
    vehicle: VehicleObject
    errors: List[VehicleError] = Field(default_factory=list)

   