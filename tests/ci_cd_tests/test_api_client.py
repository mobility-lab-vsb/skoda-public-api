import aiohttp
import pytest

from api_layer.rest_api import SkodaRestAPI, GetEndpointResult
from api_layer.exceptions import OpenApiError
from api_layer.const import TEST_BASE_URL
from api_layer.exceptions import OpenApiAuthenticationError
from models.enums import DoorsState, YesNoState, OpenCloseState, OnOffState, LockState


@pytest.mark.asyncio
async def test_get_vehicle_test_endpoint():
    """Test of the real API call to the Škoda Open API using a fake API key."""
    
    vin = "DMBGF9NY3NF032963"
    api_key = "fXXYXYYXXYHJFJDDFH"

    async with aiohttp.ClientSession() as session:
        # Api initialization
        api = SkodaRestAPI(api_key=api_key, session=session)
        api._base_url = TEST_BASE_URL

        endpoint_result = await api.get_vehicle(vin)
            
        print(f"[Success] Raw JSON: {endpoint_result.raw_json}")
        
        vehicle_data = endpoint_result.result

        assert isinstance(endpoint_result, GetEndpointResult)
        assert vehicle_data is not None
        assert vehicle_data.vehicle.vin == vin
        assert vehicle_data.vehicle.license_plate == "1AB 2345"
        assert vehicle_data.vehicle.name == "Enyaq RS"
        assert vehicle_data.vehicle.render_url == "https://mspgwlivestorage.blob.core.windows.net/demomode/enyaq_rs_coupe_green_exterior_side.png"
        assert vehicle_data.vehicle.odometer is not None
        assert vehicle_data.vehicle.status is not None

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
        print(f"\n[Success] STATUS: {vehicle_status}")

        assert isinstance(endpoint_result, GetEndpointResult)
        assert vehicle_status is not None
        
        assert vehicle_status.overall is not None
        assert vehicle_status.detail is not None
        assert isinstance(vehicle_status.car_captured_timestamp, str)
        
        assert isinstance(vehicle_status.overall.doors_locked, DoorsState)
        assert isinstance(vehicle_status.overall.locked, YesNoState)
        assert isinstance(vehicle_status.overall.doors, OpenCloseState)
        assert isinstance(vehicle_status.overall.windows, OpenCloseState)
        assert isinstance(vehicle_status.overall.lights, OnOffState)
        assert isinstance(vehicle_status.overall.reliable_lock_status, LockState)

        assert isinstance(vehicle_status.detail.sunroof, OpenCloseState)
        assert isinstance(vehicle_status.detail.trunk, OpenCloseState)
        assert isinstance(vehicle_status.detail.bonnet, OpenCloseState)