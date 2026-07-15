import aiohttp
import pytest

from api_layer.rest_api import SkodaRestAPI, GetEndpointResult
from api_layer.exceptions import OpenApiError
from api_layer.const import TEST_BASE_URL
from api_layer.exceptions import OpenApiAuthenticationError
from models.enums import DoorsState, MovementState, TemperatureUnit, YesNoState, OpenCloseState, OnOffState, LockState, AirConditioningState
from models.air_conditioning import AirConditioning 
from models.parking_position import ParkingPosition
from models.vehicle_status import VehicleStatus
from models.vehicle import Odometer

@pytest.mark.asyncio
async def test_get_vehicle_test_endpoint():
    """Test of the real API call to the Škoda Open API using a fake API key."""
    
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        # Api initialization
        api = SkodaRestAPI(api_key=api_key, session=session)
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
        api = SkodaRestAPI(api_key=api_key, session=session)
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
        api = SkodaRestAPI(api_key=api_key, session=session)
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
        api = SkodaRestAPI(api_key=api_key, session=session)
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