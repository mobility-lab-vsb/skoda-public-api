from .base_model import BaseModel
from .enums import DoorsState, LockState, OnOffState, OpenCloseState, YesNoState


class OverallVehicleStatus(BaseModel):
    """Overall status of the vehicle."""

    doors_locked: DoorsState
    locked: YesNoState
    doors: OpenCloseState
    windows: OpenCloseState
    lights: OnOffState
    reliable_lock_status: LockState | None = None


class VehicleStatusDetail(BaseModel):
    """Status of individual components of the vehicle."""

    sunroof: OpenCloseState
    trunk: OpenCloseState
    bonnet: OpenCloseState


class VehicleStatus(BaseModel):
    """Pack all the objects into one object for the vehicle status."""

    overall: OverallVehicleStatus
    detail: VehicleStatusDetail
    car_captured_timestamp: str | None = None
