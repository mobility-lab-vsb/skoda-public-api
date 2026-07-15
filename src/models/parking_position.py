from typing import Optional
from .base_model import BaseModel
from .enums import ( 
    MovementState
)

class GPRCoordinates(BaseModel):
    """GPR coordinates of the vehicle."""
    latitude: float
    longitude: float

class ParkingPosition(BaseModel):
    """Parking position information."""
    state: MovementState
    gps_coordinates: Optional[GPRCoordinates] = None
    formatted_address: Optional[str] = None

