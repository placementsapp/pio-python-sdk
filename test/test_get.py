"""
Tests for the GET method of the PlacementsIO class
"""

import re
import json
import pytest
import httpx
from pytest_httpx import HTTPXMock
from pio import PlacementsIO
from pio.model.service import services
from pio.model.response import APIResponse
from pio.error.api_error import APIError

API_SERVICES = [_ for _ in services if _ != "reports"]
URL_REGEX = r"https://api-staging\.placements\.io/v1/(\w+)(\?.*)?"


@pytest.fixture()
def mock_get_success(httpx_mock: HTTPXMock):
    """
    Mocks a successful GET request
    """

    def custom_response(request):
        match = re.match(URL_REGEX, str(request.url))
        if not match:
            raise ValueError(f"Test URL {request.url} does not match regex {URL_REGEX}")
        service = match.group(1)

        with open(f"test/data/get/{service}.json", encoding="utf-8") as response:
            return httpx.Response(status_code=200, json=json.load(response))

    httpx_mock.add_callback(custom_response)


@pytest.fixture()
def mock_get_error(httpx_mock: HTTPXMock):
    """
    Mocks a failed GET request
    """
    with open("test/data/error/400.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="GET",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=400,
        )


@pytest.fixture()
def mock_rate_limit(httpx_mock: HTTPXMock):
    """
    Mocks a rate limited GET request
    """
    with open("test/data/error/429.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="GET",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=429,
            headers={"Retry-After": "1"},
        )
    with open("test/data/get/no_results.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="GET",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=200,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("service", API_SERVICES)
async def test_get_success(service, mock_get_success):
    """Test a successful GET request"""
    pio = PlacementsIO(environment="staging", token="foo")
    pio_service = getattr(pio, service).get
    api_response = await pio_service()
    print(service, api_response)
    assert api_response
    assert isinstance(api_response, list)


@pytest.mark.asyncio
@pytest.mark.parametrize("service", API_SERVICES)
async def test_get_errors(service, mock_get_error):
    """Test a failed GET request"""
    pio = PlacementsIO(environment="staging", token="foo")
    pio_service = getattr(pio, service).get
    with pytest.raises(APIError):
        await pio_service()


@pytest.mark.asyncio
async def test_get_rate_limit(mock_rate_limit):
    """Test a rate limited GET request"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.accounts.get()
    print("API Response", api_response)
    assert isinstance(api_response, list)


# ============================================================================
# Tests for APIResponse and included resources
# ============================================================================


@pytest.fixture()
def mock_get_with_included(httpx_mock: HTTPXMock):
    """
    Mocks a GET request that returns included resources
    """
    with open("test/data/get/campaigns_with_included.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="GET",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=200,
        )


@pytest.mark.asyncio
async def test_api_response_is_list_compatible(mock_get_success):
    """Test that APIResponse is compatible with list operations"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    # Should be an instance of list (backward compatibility)
    assert isinstance(api_response, list)
    assert isinstance(api_response, APIResponse)

    # Should support len()
    assert len(api_response) >= 0

    # Should support iteration
    for item in api_response:
        assert isinstance(item, dict)

    # Should support indexing (if there are items)
    if len(api_response) > 0:
        assert isinstance(api_response[0], dict)


@pytest.mark.asyncio
async def test_api_response_has_included_property(mock_get_success):
    """Test that APIResponse has accessible included property"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    # Should have included property (empty list when no included in response)
    assert hasattr(api_response, "included")
    assert isinstance(api_response.included, list)


@pytest.mark.asyncio
async def test_api_response_has_meta_property(mock_get_success):
    """Test that APIResponse has accessible meta property"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    # Should have meta property (empty dict when no meta in response)
    assert hasattr(api_response, "meta")
    assert isinstance(api_response.meta, dict)


@pytest.mark.asyncio
async def test_included_resources_merged_to_one(mock_get_with_included):
    """Test that included resources are merged into to-one relationships"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    assert len(api_response) == 1
    campaign = api_response[0]

    # Check advertiser relationship was merged
    advertiser_data = campaign["relationships"]["advertiser"]["data"]
    assert advertiser_data["id"] == "3549"
    assert advertiser_data["type"] == "accounts"
    assert "attributes" in advertiser_data
    assert advertiser_data["attributes"]["name"] == "Test Advertiser Inc."
    assert advertiser_data["attributes"]["account-type"] == "advertiser"

    # Check opportunity relationship was merged
    opportunity_data = campaign["relationships"]["opportunity"]["data"]
    assert opportunity_data["id"] == "485396"
    assert opportunity_data["type"] == "opportunities"
    assert "attributes" in opportunity_data
    assert opportunity_data["attributes"]["name"] == "LaGuardia Inc. - New Product"
    assert opportunity_data["attributes"]["stage-name"] == "Closed Won"


@pytest.mark.asyncio
async def test_included_resources_merged_to_many(mock_get_with_included):
    """Test that included resources are merged into to-many relationships"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    campaign = api_response[0]

    # Check line-items relationship was merged (to-many)
    line_items_data = campaign["relationships"]["line-items"]["data"]
    assert len(line_items_data) == 2

    # First line item
    assert line_items_data[0]["id"] == "101"
    assert line_items_data[0]["type"] == "line_items"
    assert "attributes" in line_items_data[0]
    assert line_items_data[0]["attributes"]["name"] == "Display Banner - Homepage"

    # Second line item
    assert line_items_data[1]["id"] == "102"
    assert line_items_data[1]["type"] == "line_items"
    assert "attributes" in line_items_data[1]
    assert line_items_data[1]["attributes"]["name"] == "Display Banner - Sidebar"


@pytest.mark.asyncio
async def test_nested_relationships_merged(mock_get_with_included):
    """Test that nested relationships in included resources are also merged"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    campaign = api_response[0]

    # The opportunity has a nested relationship to account
    opportunity_data = campaign["relationships"]["opportunity"]["data"]

    # Check that the nested account relationship was also merged
    nested_account = opportunity_data["relationships"]["account"]["data"]
    assert nested_account["id"] == "3549"
    assert nested_account["type"] == "accounts"
    assert "attributes" in nested_account
    assert nested_account["attributes"]["name"] == "Test Advertiser Inc."


@pytest.mark.asyncio
async def test_included_property_accessible(mock_get_with_included):
    """Test that raw included array is accessible via property"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    # Should have 4 included resources
    assert len(api_response.included) == 4

    # Verify included types
    included_types = {item["type"] for item in api_response.included}
    assert "accounts" in included_types
    assert "opportunities" in included_types
    assert "line_items" in included_types


@pytest.mark.asyncio
async def test_meta_property_accessible(mock_get_with_included):
    """Test that meta is accessible via property"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    assert api_response.meta["record-count"] == 1
    assert api_response.meta["page-count"] == 1


@pytest.mark.asyncio
async def test_empty_included_does_not_break(mock_get_success):
    """Test that responses without included array work correctly"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    # Should work without included
    assert isinstance(api_response, list)
    assert api_response.included == []

    # Relationships should be preserved but not merged
    if len(api_response) > 0:
        campaign = api_response[0]
        if "relationships" in campaign and "advertiser" in campaign["relationships"]:
            advertiser_data = campaign["relationships"]["advertiser"]["data"]
            # Should only have type and id (not merged attributes)
            assert "type" in advertiser_data
            assert "id" in advertiser_data


@pytest.mark.asyncio
async def test_api_response_repr(mock_get_with_included):
    """Test APIResponse string representation"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.campaigns.get()

    repr_str = repr(api_response)
    assert "APIResponse" in repr_str
    assert "1 items" in repr_str
    assert "included=4 items" in repr_str


# ============================================================================
# Tests for sparse fieldsets query parameters
# ============================================================================


@pytest.fixture()
def mock_get_capture_request(httpx_mock: HTTPXMock):
    """
    Mocks a GET request and captures the request for inspection
    """
    captured_requests = []

    def custom_response(request):
        captured_requests.append(request)
        return httpx.Response(status_code=200, json={"data": [], "meta": {}})

    httpx_mock.add_callback(custom_response)
    return captured_requests


@pytest.mark.asyncio
async def test_fields_list_sends_correct_query_param(mock_get_capture_request):
    """Test that fields as list sends correct query parameter"""
    pio = PlacementsIO(environment="staging", token="foo")
    await pio.campaigns.get(fields=["name", "id"])

    request = mock_get_capture_request[0]
    params = dict(request.url.params)
    assert params["fields[campaigns]"] == "name,id"


@pytest.mark.asyncio
async def test_fields_dict_sends_multiple_query_params(mock_get_capture_request):
    """Test that fields as dict sends query params for each entity type"""
    pio = PlacementsIO(environment="staging", token="foo")
    await pio.campaigns.get(fields={
        "campaigns": ["name", "ad-server-info"],
        "accounts": ["custom-fields"]
    })

    request = mock_get_capture_request[0]
    params = dict(request.url.params)
    assert params["fields[campaigns]"] == "name,ad-server-info"
    assert params["fields[accounts]"] == "custom-fields"


@pytest.mark.asyncio
async def test_fields_dict_normalizes_underscores_in_request(mock_get_capture_request):
    """Test that underscores in field keys are normalized to hyphens in request"""
    pio = PlacementsIO(environment="staging", token="foo")
    await pio.line_items.get(fields={
        "line_items": ["name", "start-date"],
        "campaigns": ["id"]
    })

    request = mock_get_capture_request[0]
    params = dict(request.url.params)
    assert params["fields[line-items]"] == "name,start-date"
    assert params["fields[campaigns]"] == "id"


@pytest.mark.asyncio
async def test_fields_with_include_sends_both_params(mock_get_capture_request):
    """Test that fields and include can be used together"""
    pio = PlacementsIO(environment="staging", token="foo")
    await pio.campaigns.get(
        include=["advertiser"],
        fields={
            "campaigns": ["name"],
            "accounts": ["custom-fields"]
        }
    )

    request = mock_get_capture_request[0]
    params = dict(request.url.params)
    assert params["include"] == "advertiser"
    # Include is merged into primary resource's fields to ensure relationship data is returned
    assert params["fields[campaigns]"] == "name,advertiser"
    assert params["fields[accounts]"] == "custom-fields"
