from pydantic import Field

from .active_ventilation import ActiveVentilation
from .air_conditioning import AirConditioning
from .auxiliary_heating import AuxiliaryHeating
from .base_model import BaseModel
from .charging import Charging
from .charging_profiles import ChargingProfiles
from .common import VehicleError
from .driving_range import FuelStatus
from .enums import OpenCloseState, VehicleCapability, VehicleOperationName
from .parking_position import ParkingPosition
from .vehicle_status import VehicleStatus

# Capabilities whose top-level API field can report a transient
# "<FEATURE>_UNAVAILABLE" error (as opposed to a permanent "_UNSUPPORTED" or
# "_DISABLED" one) in VehicleResponse.errors. These must still be treated as
# supported when their field is empty for that reason, otherwise a temporary
# hiccup in a single response would hide the capability for consumers that
# only evaluate it once (e.g. to decide which entities to create at setup).
_TRANSIENT_ERROR_PREFIXES: dict[VehicleCapability, str] = {
    VehicleCapability.STATUS: "VEHICLE_STATUS",
    VehicleCapability.ODOMETER: "ODOMETER",
    VehicleCapability.PARKING_POSITION: "PARKING_POSITION",
    VehicleCapability.CHARGING: "CHARGING",
    VehicleCapability.CHARGING_PROFILES: "CHARGING_PROFILES",
    VehicleCapability.AIR_CONDITIONING: "AIR_CONDITIONING",
    VehicleCapability.ACTIVE_VENTILATION: "ACTIVE_VENTILATION",
    VehicleCapability.AUXILIARY_HEATING: "AUXILIARY_HEATING",
    VehicleCapability.FUEL_STATUS: "FUEL_STATUS",
}

_VEHICLE_TYPE_CAPABILITIES: dict[str, VehicleCapability] = {
    "HYBRID": VehicleCapability.VEHICLE_TYPE_HYBRID,
    "GASOLINE": VehicleCapability.VEHICLE_TYPE_GASOLINE,
    "DIESEL": VehicleCapability.VEHICLE_TYPE_DIESEL,
    "CNG": VehicleCapability.VEHICLE_TYPE_CNG,
    "LPG": VehicleCapability.VEHICLE_TYPE_LPG,
}


class Odometer(BaseModel):
    """Odometer of the vehicle."""

    mileage_in_km: int
    car_captured_timestamp: str | None = None


class VehicleOperation(BaseModel):
    """A remote operation the vehicle supports."""

    name: VehicleOperationName


class VehicleObject(BaseModel):
    """Pack whole vehicle object into one object for the vehicle."""

    name: str | None = None
    vin: str
    license_plate: str | None = None
    render_url: str | None = None
    odometer: Odometer | None = None
    status: VehicleStatus | None = None
    parking_position: ParkingPosition | None = None
    auxiliary_heating: AuxiliaryHeating | None = None
    active_ventilation: ActiveVentilation | None = None
    air_conditioning: AirConditioning | None = None
    fuel_status: FuelStatus | None = None
    charging: Charging | None = None
    charging_profiles: ChargingProfiles | None = None
    operations: list[VehicleOperation] | None = None


class VehicleResponse(BaseModel):
    """Response object for vehicle data."""

    vehicle: VehicleObject
    errors: list[VehicleError] = Field(default_factory=list)

    def supported_capabilities(self) -> set[VehicleCapability]:
        """Determine which capabilities this vehicle supports.

        A field being absent from the response can mean the vehicle doesn't
        support it at all, or that fetching it temporarily failed (a
        "<FEATURE>_UNAVAILABLE" error). The latter must still count as
        supported, otherwise a single transient hiccup would hide the
        capability for consumers that only evaluate it once.
        """
        vehicle = self.vehicle
        caps: set[VehicleCapability] = set()
        unavailable_prefixes = {
            error.type.rsplit("_", 1)[0]
            for error in self.errors
            if error.type.endswith("_UNAVAILABLE")
        }

        def supported(capability: VehicleCapability, present: bool) -> bool:
            prefix = _TRANSIENT_ERROR_PREFIXES.get(capability)
            return present or (prefix is not None and prefix in unavailable_prefixes)

        if supported(VehicleCapability.STATUS, vehicle.status is not None):
            caps.add(VehicleCapability.STATUS)
            if (
                vehicle.status is not None
                and vehicle.status.detail.sunroof != OpenCloseState.UNSUPPORTED
            ):
                caps.add(VehicleCapability.SUNROOF)
        if supported(VehicleCapability.ODOMETER, vehicle.odometer is not None):
            caps.add(VehicleCapability.ODOMETER)
        if supported(
            VehicleCapability.PARKING_POSITION, vehicle.parking_position is not None
        ):
            caps.add(VehicleCapability.PARKING_POSITION)
        if supported(VehicleCapability.CHARGING, vehicle.charging is not None):
            caps.add(VehicleCapability.CHARGING)
        if supported(
            VehicleCapability.CHARGING_PROFILES, vehicle.charging_profiles is not None
        ):
            caps.add(VehicleCapability.CHARGING_PROFILES)
        if supported(
            VehicleCapability.AIR_CONDITIONING, vehicle.air_conditioning is not None
        ):
            caps.add(VehicleCapability.AIR_CONDITIONING)
        if supported(
            VehicleCapability.AUXILIARY_HEATING, vehicle.auxiliary_heating is not None
        ):
            caps.add(VehicleCapability.AUXILIARY_HEATING)
        if supported(
            VehicleCapability.ACTIVE_VENTILATION,
            vehicle.active_ventilation is not None,
        ):
            caps.add(VehicleCapability.ACTIVE_VENTILATION)

        fuel_status = vehicle.fuel_status
        if supported(VehicleCapability.FUEL_STATUS, fuel_status is not None):
            caps.add(VehicleCapability.FUEL_STATUS)

        if fuel_status is not None:
            if fuel_status.ad_blue_range is not None:
                caps.add(VehicleCapability.AD_BLUE_RANGE)

            engine_types = {
                (engine.engine_type or "").upper()
                for engine in (
                    fuel_status.primary_engine_range,
                    fuel_status.secondary_engine_range,
                )
                if engine is not None
            }
            if "ELECTRIC" in engine_types:
                caps.add(VehicleCapability.VEHICLE_TYPE_ELECTRIC)

            car_type_capability = _VEHICLE_TYPE_CAPABILITIES.get(
                (fuel_status.car_type or "").upper()
            )
            if car_type_capability is not None:
                caps.add(car_type_capability)

        return caps

    def supported_operations(self) -> set[VehicleOperationName] | None:
        """Return the remote operations this vehicle supports.

        Returns None when the response carries no operations list (for example
        when it reports OPERATIONS_UNAVAILABLE), so callers can tell "unknown"
        apart from "supports nothing". Operations this library does not know
        yet are left out.
        """
        if self.vehicle.operations is None:
            return None
        return {
            operation.name
            for operation in self.vehicle.operations
            if operation.name is not VehicleOperationName.UNKNOWN
        }
