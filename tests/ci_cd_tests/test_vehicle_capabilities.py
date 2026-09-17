from skoda_public_api.models.common import VehicleError
from skoda_public_api.models.driving_range import EngineRange, FuelStatus
from skoda_public_api.models.enums import (
    DoorsState,
    OnOffState,
    OpenCloseState,
    VehicleCapability,
    VehicleErrorState,
    YesNoState,
)
from skoda_public_api.models.vehicle import VehicleObject, VehicleResponse
from skoda_public_api.models.vehicle_status import (
    OverallVehicleStatus,
    VehicleStatus,
    VehicleStatusDetail,
)

VIN = "TMBJM7NP2M1TMP511"


def _vehicle_status(sunroof: OpenCloseState = OpenCloseState.CLOSED) -> VehicleStatus:
    """Build a minimal, valid VehicleStatus with the given sunroof state."""
    return VehicleStatus(
        overall=OverallVehicleStatus(
            doors_locked=DoorsState.NO,
            locked=YesNoState.YES,
            doors=OpenCloseState.CLOSED,
            windows=OpenCloseState.CLOSED,
            lights=OnOffState.OFF,
        ),
        detail=VehicleStatusDetail(
            sunroof=sunroof,
            trunk=OpenCloseState.CLOSED,
            bonnet=OpenCloseState.CLOSED,
        ),
    )


def _vehicle(**overrides: object) -> VehicleObject:
    """Build a VehicleObject, skipping validation so tests only need to set the fields under test."""
    defaults: dict[str, object] = {
        "vin": VIN,
        "odometer": None,
        "status": None,
        "parking_position": None,
        "auxiliary_heating": None,
        "active_ventilation": None,
        "air_conditioning": None,
        "fuel_status": None,
        "charging": None,
        "charging_profiles": None,
    }
    defaults.update(overrides)
    return VehicleObject.model_construct(**defaults)


def _response(
    vehicle: VehicleObject, errors: list[VehicleError] | None = None
) -> VehicleResponse:
    return VehicleResponse.model_construct(vehicle=vehicle, errors=errors or [])


def test_supported_capabilities_electric_vehicle_with_sunroof() -> None:
    """A fully-equipped EV reports status, sunroof, charging and the electric car type."""
    vehicle = _vehicle(
        status=_vehicle_status(sunroof=OpenCloseState.OPEN),
        odometer=object(),
        parking_position=object(),
        charging=object(),
        charging_profiles=object(),
        air_conditioning=object(),
        fuel_status=FuelStatus(
            primary_engine_range=EngineRange(engine_type="ELECTRIC")
        ),
    )

    caps = _response(vehicle).supported_capabilities()

    assert caps == {
        VehicleCapability.STATUS,
        VehicleCapability.SUNROOF,
        VehicleCapability.ODOMETER,
        VehicleCapability.PARKING_POSITION,
        VehicleCapability.CHARGING,
        VehicleCapability.CHARGING_PROFILES,
        VehicleCapability.AIR_CONDITIONING,
        VehicleCapability.FUEL_STATUS,
        VehicleCapability.VEHICLE_TYPE_ELECTRIC,
    }


def test_sunroof_not_reported_when_vehicle_lacks_one() -> None:
    """A vehicle whose status detail marks the sunroof UNSUPPORTED must not report the capability."""
    vehicle = _vehicle(status=_vehicle_status(sunroof=OpenCloseState.UNSUPPORTED))

    caps = _response(vehicle).supported_capabilities()

    assert VehicleCapability.STATUS in caps
    assert VehicleCapability.SUNROOF not in caps


def test_diesel_vehicle_reports_car_type_and_ad_blue() -> None:
    """A diesel vehicle reports its fuel type and AdBlue range, but not an electric car type."""
    vehicle = _vehicle(
        fuel_status=FuelStatus(
            car_type="DIESEL",
            ad_blue_range=6000,
            primary_engine_range=EngineRange(engine_type="DIESEL"),
        )
    )

    caps = _response(vehicle).supported_capabilities()

    assert caps == {
        VehicleCapability.FUEL_STATUS,
        VehicleCapability.VEHICLE_TYPE_DIESEL,
        VehicleCapability.AD_BLUE_RANGE,
    }


def test_missing_fuel_status_reports_no_engine_capabilities() -> None:
    """A vehicle without fuel status data reports none of the fuel/engine capabilities."""
    vehicle = _vehicle()

    caps = _response(vehicle).supported_capabilities()

    assert caps == set()


def test_transient_unavailable_error_still_counts_as_supported() -> None:
    """A transient '_UNAVAILABLE' error must not hide a capability that is genuinely supported."""
    vehicle = _vehicle(charging=None)
    errors = [
        VehicleError(
            type=VehicleErrorState.CHARGING_UNAVAILABLE, description="temporary"
        )
    ]

    caps = _response(vehicle, errors).supported_capabilities()

    assert VehicleCapability.CHARGING in caps


def test_permanently_unsupported_field_is_not_reported() -> None:
    """A missing field with no matching transient error is treated as genuinely unsupported."""
    vehicle = _vehicle(charging=None)
    errors = [
        VehicleError(
            type=VehicleErrorState.CHARGING_UNSUPPORTED, description="not supported"
        )
    ]

    caps = _response(vehicle, errors).supported_capabilities()

    assert VehicleCapability.CHARGING not in caps
