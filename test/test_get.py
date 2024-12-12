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
