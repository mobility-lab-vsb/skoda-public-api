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
        #Test instance objects
        assert vehicle_data.vehicle.odometer is None or isinstance(
            vehicle_data.vehicle.odometer, Odometer
        )
        assert vehicle_data.vehicle.status is None or isinstance(
            vehicle_data.vehicle.status, VehicleStatus
        )
        assert vehicle_data.vehicle.air_conditioning is None or isinstance(
            vehicle_data.vehicle.air_conditioning, AirConditioning
        )
        assert vehicle_data.vehicle.parking_position is None or isinstance(
            vehicle_data.vehicle.parking_position, ParkingPosition
        )

        #TODO (David): add there other objects from issue 19

        #assert vehicle_data.vehicle.auxiliary_heating is not None - Uncomment when the real endpoint will be functional
        #assert vehicle_data.vehicle.active_ventilation is not None - Uncomment when the real endpoint will be functional

@pytest.mark.asyncio
async def test_get_vehicle_status_test_endpoint():
    """Test of the real API call to the Škoda Open API for vehicle status using a fake API key."""
    
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        api = SkodaRestAPI(api_key="", session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_vehicle_status(vin)
        
        vehicle_status = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert vehicle_status is not None
        
        assert vehicle_status.overall is not None
        assert vehicle_status.detail is not None
        #Can be null (marked Optional)
        assert vehicle_status.car_captured_timestamp is None or isinstance(
           vehicle_status.car_captured_timestamp, str
        )
        
        assert isinstance(vehicle_status.overall.doors_locked, DoorsState)
        assert isinstance(vehicle_status.overall.locked, YesNoState)
        assert isinstance(vehicle_status.overall.doors, OpenCloseState)
        assert isinstance(vehicle_status.overall.windows, OpenCloseState)
        assert isinstance(vehicle_status.overall.lights, OnOffState)
        assert vehicle_status.overall.reliable_lock_status is None or isinstance(
            vehicle_status.overall.reliable_lock_status, LockState
        )

        assert isinstance(vehicle_status.detail.sunroof, OpenCloseState)
        assert isinstance(vehicle_status.detail.trunk, OpenCloseState)
        assert isinstance(vehicle_status.detail.bonnet, OpenCloseState)

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
    
        assert isinstance(air_conditioning.state, AirConditioningState)  
        
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
            assert isinstance(air_conditioning.target_temperature.unit, TemperatureUnit)
            
        # Window Heating Attribs
        if air_conditioning.window_heating is not None:
            assert air_conditioning.window_heating.enabled is None or isinstance(
                air_conditioning.window_heating.enabled, bool
            )
            assert air_conditioning.window_heating.front is None or isinstance(
                air_conditioning.window_heating.front, OnOffState
            )
            assert air_conditioning.window_heating.rear is None or isinstance(
                air_conditioning.window_heating.rear, OnOffState
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

        assert isinstance(parking_pos.state, MovementState)

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
        assert charging is not None
        
        
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
            assert charging.status.state is None or isinstance(
                charging.status.state, ChargingState
            )
            assert charging.status.charge_type is None or isinstance(
                charging.status.charge_type, ChargeType
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
                charging.settings.preferred_charge_mode, ChargeMode
            )
            
            # List of available charge modes
            assert charging.settings.available_charge_modes is None or isinstance(
                charging.settings.available_charge_modes, list
            )
            if charging.settings.available_charge_modes is not None:
                assert all(isinstance(mode, ChargeMode) for mode in charging.settings.available_charge_modes)
                
            assert charging.settings.charging_care_mode is None or isinstance(
                charging.settings.charging_care_mode, ChargeCareModeState
            )
            assert charging.settings.auto_unlock_plug_when_charged is None or isinstance(
                charging.settings.auto_unlock_plug_when_charged, AutoUnlockPlugState
            )
            assert charging.settings.max_charge_current_ac is None or isinstance(
                charging.settings.max_charge_current_ac, MaxChargeCurrentAcState
            )
            assert charging.settings.max_charge_current_ac_ampere is None or isinstance(
                charging.settings.max_charge_current_ac_ampere, int
            )