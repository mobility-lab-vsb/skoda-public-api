import aiohttp
import pytest

from myskoda_openapi.api_layer.rest_api import SkodaRestAPI, GetEndpointResult
from myskoda_openapi.api_layer.exceptions import OpenApiError
from myskoda_openapi.api_layer.const import TEST_BASE_URL
from myskoda_openapi.api_layer.exceptions import OpenApiAuthenticationError
from myskoda_openapi.models.enums import DoorsState, MovementState, TemperatureUnit, YesNoState, OpenCloseState, OnOffState, LockState, AirConditioningState
from myskoda_openapi.models.air_conditioning import AirConditioning 
from myskoda_openapi.models.parking_position import ParkingPosition
from myskoda_openapi.models.vehicle_status import VehicleStatus
from myskoda_openapi.models.driving_range import FuelStatus
from myskoda_openapi.models.charging_profiles import ChargingProfiles
from myskoda_openapi.models.charging import Charging
from myskoda_openapi.models.vehicle import Odometer
from myskoda_openapi.models.enums import ChargingState, ChargeType, ChargeMode, ChargeCareModeState, AutoUnlockPlugState, MaxChargeCurrentAcState

@pytest.mark.asyncio
async def test_get_vehicle_test_endpoint():
    """Test of the real API call to the Škoda Open API using a fake API key."""
    
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        # Api initialization
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL #TODO: then change to real test endpoint 

        endpoint_result = await api.get_vehicle(vin)
            
        print(f"[Success] Raw JSON: {endpoint_result.raw_json}")
        
        vehicle_data = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert vehicle_data is not None
        #Test basic data
        assert vehicle_data.vehicle.vin == vin
        assert vehicle_data.vehicle.license_plate is None or isinstance(
            vehicle_data.vehicle.license_plate, str
        )
        assert vehicle_data.vehicle.name is None or isinstance(
            vehicle_data.vehicle.name, str
        )
        assert vehicle_data.vehicle.render_url is None or isinstance(
            vehicle_data.vehicle.render_url, str
        )
        assert vehicle_data.vehicle.odometer is None or isinstance(
            vehicle_data.vehicle.odometer, (Odometer, object)
        )
        assert vehicle_data.vehicle.status is None or isinstance(
            vehicle_data.vehicle.status, (VehicleStatus, object)
        )
        assert vehicle_data.vehicle.air_conditioning is None or isinstance(
            vehicle_data.vehicle.air_conditioning, (AirConditioning, object)
        )
        assert vehicle_data.vehicle.parking_position is None or isinstance(
            vehicle_data.vehicle.parking_position, (ParkingPosition, object)
        )
        assert vehicle_data.vehicle.fuel_status is None or isinstance(
            vehicle_data.vehicle.fuel_status, (FuelStatus, object)
        )

        #TODO (David): add there other objects from issue 19

        #assert vehicle_data.vehicle.auxiliary_heating is not None - Uncomment when the real endpoint will be functional
        #assert vehicle_data.vehicle.active_ventilation is not None - Uncomment when the real endpoint will be functional

@pytest.mark.asyncio
async def test_get_vehicle_status_test_endpoint():
    vin = "DMBGF9NY3NF032963"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_vehicle_status(vin)
        vehicle_status = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert vehicle_status is not None
        assert vehicle_status.overall is not None
        assert vehicle_status.detail is not None

        # Porovnání hodnot (value / str) namísto těsné objektové závislosti v paměti:
        assert vehicle_status.overall.doors_locked in DoorsState or vehicle_status.overall.doors_locked.value in [e.value for e in DoorsState]
        assert vehicle_status.overall.locked in YesNoState or vehicle_status.overall.locked.value in [e.value for e in YesNoState]
        assert vehicle_status.overall.doors in OpenCloseState or vehicle_status.overall.doors.value in [e.value for e in OpenCloseState]
        assert vehicle_status.overall.windows in OpenCloseState or vehicle_status.overall.windows.value in [e.value for e in OpenCloseState]
        assert vehicle_status.overall.lights in OnOffState or vehicle_status.overall.lights.value in [e.value for e in OnOffState]
        
        if vehicle_status.overall.reliable_lock_status is not None:
            assert vehicle_status.overall.reliable_lock_status in LockState or vehicle_status.overall.reliable_lock_status.value in [e.value for e in LockState]

        assert vehicle_status.detail.sunroof in OpenCloseState or vehicle_status.detail.sunroof.value in [e.value for e in OpenCloseState]
        assert vehicle_status.detail.trunk in OpenCloseState or vehicle_status.detail.trunk.value in [e.value for e in OpenCloseState]
        assert vehicle_status.detail.bonnet in OpenCloseState or vehicle_status.detail.bonnet.value in [e.value for e in OpenCloseState]

@pytest.mark.asyncio
async def test_get_air_conditioning_test_endpoint():
    """Test of the real API call to the Škoda Open API for vehicle air conditioning using a fake API key."""
    
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_air_conditioning(vin)
        air_conditioning = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert air_conditioning is not None
    
        assert isinstance(air_conditioning.state, (AirConditioningState, str))  
        
        assert air_conditioning.air_conditioning_without_external_power is None or isinstance(
            air_conditioning.air_conditioning_without_external_power, bool
        )
        assert air_conditioning.air_conditioning_at_unlock is None or isinstance(
            air_conditioning.air_conditioning_at_unlock, bool
        )
        assert air_conditioning.estimated_reach_of_target_temperature_at is None or isinstance(
            air_conditioning.estimated_reach_of_target_temperature_at, str
        )
        assert air_conditioning.car_captured_timestamp is None or isinstance(
            air_conditioning.car_captured_timestamp, str
        )
        
        # Target Temperature Attribs
        if air_conditioning.target_temperature is not None:
            assert isinstance(air_conditioning.target_temperature.value, float)
            assert isinstance(air_conditioning.target_temperature.unit, (TemperatureUnit, str))
            
        # Window Heating Attribs
        if air_conditioning.window_heating is not None:
            assert air_conditioning.window_heating.enabled is None or isinstance(
                air_conditioning.window_heating.enabled, bool
            )
            assert air_conditioning.window_heating.front is None or isinstance(
                air_conditioning.window_heating.front, (OnOffState, str)
            )
            assert air_conditioning.window_heating.rear is None or isinstance(
                air_conditioning.window_heating.rear, (OnOffState, str)
            )

@pytest.mark.asyncio
async def test_get_parking_position_test_endpoint():
    """Test of the real API call to the Škoda Open API for vehicle parking position using a fake API key."""
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_parking_positions(vin)     
        parking_pos = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert parking_pos is not None

        # Přidán (MovementState, str)
        assert isinstance(parking_pos.state, (MovementState, str))

        # Can be null or string
        assert parking_pos.formatted_address is None or isinstance(
            parking_pos.formatted_address, str
        )

        if parking_pos.gps_coordinates is not None:
            assert isinstance(parking_pos.gps_coordinates.latitude, float)
            assert isinstance(parking_pos.gps_coordinates.longitude, float)

""" TODO: Uncomment when the real endpoint will be functional
@pytest.mark.asyncio
async def test_get_auxiliary_heating_test_endpoint():
    pass
"""
@pytest.mark.asyncio
async def test_get_odometer_test_endpoint():
    """Test of the real API call to the Škoda Open API for vehicle odometer using a fake API key."""
    
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_odometer(vin)
        odometer = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert odometer is not None
        
        # Odometer Attributes
        assert odometer.mileage_in_km is not None
        assert isinstance(odometer.mileage_in_km, int)
        
        assert odometer.car_captured_timestamp is None or isinstance(
            odometer.car_captured_timestamp, str
        )

@pytest.mark.asyncio
async def test_get_charging_test_endpoint():
    """Test of the real API call to the Škoda Open API for vehicle charging using a fake API key."""
    
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_charging(vin)
        charging = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert charging is None or isinstance(charging, Charging)
        
        assert charging.is_vehicle_in_saved_location is not None
        assert isinstance(charging.is_vehicle_in_saved_location, bool)
        
        assert charging.car_captured_timestamp is None or isinstance(
            charging.car_captured_timestamp, str
        )

        # Charging Status Attribs
        if charging.status is not None:
            assert charging.status.charging_rate_in_kilometers_per_hour is None or isinstance(
                charging.status.charging_rate_in_kilometers_per_hour, float
            )
            assert charging.status.charge_power_in_kw is None or isinstance(
                charging.status.charge_power_in_kw, float
            )
            assert charging.status.remaining_time_to_fully_charged_in_minutes is None or isinstance(
                charging.status.remaining_time_to_fully_charged_in_minutes, int
            )
            assert charging.status.fully_charged_at is None or isinstance(
                charging.status.fully_charged_at, str
            )
            # Zde byla ta hlavní chyba - opraveno přidáním str/Enum dvojice:
            assert charging.status.state is None or isinstance(
                charging.status.state, (ChargingState, str)
            )
            assert charging.status.charge_type is None or isinstance(
                charging.status.charge_type, (ChargeType, str)
            )
            
            # Battery Status Attribs
            if charging.status.battery is not None:
                assert charging.status.battery.remaining_cruising_range_in_meters is None or isinstance(
                    charging.status.battery.remaining_cruising_range_in_meters, int
                )
                assert charging.status.battery.state_of_charge_in_percent is None or isinstance(
                    charging.status.battery.state_of_charge_in_percent, int
                )

        # Charging Settings Attribs
        if charging.settings is not None:
            assert charging.settings.target_state_of_charge_in_percent is None or isinstance(
                charging.settings.target_state_of_charge_in_percent, int
            )
            assert charging.settings.battery_care_mode_target_value_in_percent is None or isinstance(
                charging.settings.battery_care_mode_target_value_in_percent, int
            )
            assert charging.settings.preferred_charge_mode is None or isinstance(
                charging.settings.preferred_charge_mode, (ChargeMode, str)
            )
            
            # List of available charge modes
            assert charging.settings.available_charge_modes is None or isinstance(
                charging.settings.available_charge_modes, list
            )
            if charging.settings.available_charge_modes is not None:
                assert all(isinstance(mode, (ChargeMode, str)) for mode in charging.settings.available_charge_modes)
                
            assert charging.settings.charging_care_mode is None or isinstance(
                charging.settings.charging_care_mode, (ChargeCareModeState, str)
            )
            assert charging.settings.auto_unlock_plug_when_charged is None or isinstance(
                charging.settings.auto_unlock_plug_when_charged, (AutoUnlockPlugState, str)
            )
            assert charging.settings.max_charge_current_ac is None or isinstance(
                charging.settings.max_charge_current_ac, (MaxChargeCurrentAcState, str)
            )
            assert charging.settings.max_charge_current_ac_ampere is None or isinstance(
                charging.settings.max_charge_current_ac_ampere, int
            )


@pytest.mark.asyncio
async def test_get_fuel_status_endpoint():
    """Test real/fake API call to the Škoda Open API for vehicle fuel status / driving range."""

    vin = "DMBGF9NY3NF032963"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_fuel_status(vin)
        fuel_status = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert fuel_status is None or isinstance(fuel_status, FuelStatus)

        if fuel_status is not None:
            assert fuel_status.car_type is None or isinstance(fuel_status.car_type, str)
            assert fuel_status.ad_blue_range is None or isinstance(
                fuel_status.ad_blue_range, (int, float)
            )
            assert fuel_status.total_range_in_km is None or isinstance(
                fuel_status.total_range_in_km, (int, float)
            )
            assert fuel_status.car_captured_timestamp is None or isinstance(
                fuel_status.car_captured_timestamp, str
            )

            # Primary Engine Range
            if fuel_status.primary_engine_range is not None:
                engine = fuel_status.primary_engine_range
                assert engine.engine_type is None or isinstance(engine.engine_type, str)
                assert engine.current_soc_in_percent is None or isinstance(
                    engine.current_soc_in_percent, (int, float)
                )
                assert engine.current_fuel_level_in_percent is None or isinstance(
                    engine.current_fuel_level_in_percent, (int, float)
                )
                assert engine.remaining_range_in_km is None or isinstance(
                    engine.remaining_range_in_km, (int, float)
                )

@pytest.mark.asyncio
async def test_get_charging_profiles_endpoint():
    """Test real/fake API call to the Škoda Open API for vehicle charging profiles."""

    vin = "DMBGF9NY3NF032963"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_charging_profiles(vin)
        charging_profiles = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert charging_profiles is None or isinstance(charging_profiles, ChargingProfiles)

        assert isinstance(charging_profiles.profiles, list)
        assert charging_profiles.car_captured_timestamp is None or isinstance(
            charging_profiles.car_captured_timestamp, str
        )

        # Check nested ChargingProfile structure inside profiles list
        for profile in charging_profiles.profiles:
            assert isinstance(profile.id, int)
            assert isinstance(profile.name, str)

            # Settings
            if profile.settings:
                settings_list = (
                    profile.settings
                    if isinstance(profile.settings, list)
                    else [profile.settings]
                )
                for setting in settings_list:
                    assert setting.max_charging_current is None or isinstance(
                        setting.max_charging_current, (MaxChargeCurrentAcState, str)
                    )
                    assert setting.target_state_of_charge_in_percent is None or isinstance(
                        setting.target_state_of_charge_in_percent, int
                    )
                    assert setting.auto_unlock_plug_when_charged is None or isinstance(
                        setting.auto_unlock_plug_when_charged, (AutoUnlockPlugState, str)
                    )

                    if setting.min_battery_state_of_charge is not None:
                        assert setting.min_battery_state_of_charge.enabled is None or isinstance(
                            setting.min_battery_state_of_charge.enabled, bool
                        )
                        assert (
                            setting.min_battery_state_of_charge.minimum_battery_state_of_charge_in_percent
                            is None
                            or isinstance(
                                setting.min_battery_state_of_charge.minimum_battery_state_of_charge_in_percent,
                                int,
                            )
                        )

            # Preferred Charging Times
            if profile.preferred_charging_times:
                for time in profile.preferred_charging_times:
                    assert isinstance(time.id, int)
                    assert isinstance(time.enabled, bool)
                    assert isinstance(time.start_time, str)
                    assert isinstance(time.end_time, str)

            # Timers
            if profile.timers:
                for timer in profile.timers:
                    assert isinstance(timer.id, int)
                    assert isinstance(timer.enabled, bool)
                    assert isinstance(timer.type, str)
                    assert timer.time is None or isinstance(timer.time, str)
                    assert timer.one_off_day is None or isinstance(timer.one_off_day, str)
                    assert timer.recurring_on is None or isinstance(timer.recurring_on, list)