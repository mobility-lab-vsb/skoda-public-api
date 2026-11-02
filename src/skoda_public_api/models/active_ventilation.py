from .base_model import BaseModel
from .enums import VentilationState


class ActiveVentilation(BaseModel):
    """Active ventilation status."""

    state: VentilationState
    duration_in_seconds: int | None = None
    car_captured_timestamp: str | None = None
