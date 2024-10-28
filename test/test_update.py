"""
Tests for the UPDATE method of the PlacementsIO class
"""

import re
import json
from unittest.mock import patch
import pytest
import httpx
from pytest_httpx import HTTPXMock
from pio import PlacementsIO
from pio.model.service import services

URL_REGEX = r"https://api-staging\.placements\.io/v1/(\w+)(\?.*)?"


@pytest.fixture()
def mock_update_success(httpx_mock: HTTPXMock):
    """
    Mocks a successful UPDATE request
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
def mock_update_error(httpx_mock: HTTPXMock):
    """
    Mocks a failed UPDATE request
    """
    with open("test/data/error/400.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="PATCH",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=400,
        )


@pytest.fixture()
def mock_rate_limit(httpx_mock: HTTPXMock):
    """
    Mocks a rate limited UPDATE request
    """
    with open("test/data/error/429.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="PATCH",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=429,
            headers={"Retry-After": "1"},
        )
    with open("test/data/get/no_results.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="PATCH",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=200,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("service", services)
async def test_update_success(service, mock_update_success):
    """Tests a successful update request"""
    pio = PlacementsIO(environment="staging", token="foo")
    pio_service = getattr(pio, service).update
    api_response = await pio_service(resource_ids=[1], attributes={"foo": "bar"})
    print(service, api_response)
    assert api_response
    assert isinstance(api_response, list)


@pytest.mark.asyncio
@pytest.mark.parametrize("service", services)
async def test_update_errors(service, mock_update_error):
    """Tests an update request that returns errors"""
    pio = PlacementsIO(environment="staging", token="foo")
    pio_service = getattr(pio, service).update
    api_response = await pio_service(resource_ids=[1], attributes={"foo": "bar"})
    print(service, api_response)
    assert api_response
    assert isinstance(api_response, list)
    assert api_response[0].get("errors")


@pytest.mark.asyncio
async def test_update_rate_limit(mock_rate_limit):
    """Tests an update request that is rate limited"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.accounts.update(
        resource_ids=[1], attributes={"foo": "bar"}
    )
    print("API Response", api_response)
    assert isinstance(api_response, list)


@patch("httpx.AsyncClient.request")
@pytest.mark.asyncio
async def test_update_with_static_attributes_relationships(mock_request):
    """Tests an update request with static attributes and relationships"""
    with open("test/data/get/accounts.json", encoding="utf-8") as response:
        mock_request.return_value = httpx.Response(
            status_code=200, json=json.load(response)
        )

    pio = PlacementsIO(environment="staging", token="foo")
    attributes = {"foo": "bar", "baz": {"nested": "value"}}
    relationships = {"product": {"data": {"type": "products", "id": 1}}}
    print("Static Attributes", attributes)
    print("Static Relationships", relationships)
    await pio.accounts.update(
        resource_ids=[1], attributes=attributes, relationships=relationships
    )
    assert (
        json.loads(mock_request.call_args.kwargs["data"])["data"]["attributes"]
        == attributes
    )
    assert (
        json.loads(mock_request.call_args.kwargs["data"])["data"]["relationships"]
        == relationships
    )


@patch("httpx.AsyncClient.request")
@pytest.mark.asyncio
async def test_update_with_dynamic_attributes_relationships(mock_request):
    """Tests an update request with dynamic attributes and relationships"""
    with open("test/data/get/accounts.json", encoding="utf-8") as response:
        mock_request.return_value = httpx.Response(
            status_code=200, json=json.load(response)
        )

    pio = PlacementsIO(environment="staging", token="foo")

    async def attributes(resource_id):
        return {"foo": "bar", "baz": {"nested": resource_id * 5}}

    async def relationships(resource_id):
        return {"product": {"data": {"type": "products", "id": resource_id * 5}}}

    expected_attributes = await attributes(2)
    expected_relationships = await relationships(2)
    print("Dynamic Attributes", expected_attributes)
    print("Dynamic Relationships", expected_relationships)

    await pio.accounts.update(
        resource_ids=[2], attributes=attributes, relationships=relationships
    )
    assert (
        json.loads(mock_request.call_args.kwargs["data"])["data"]["attributes"]
        == expected_attributes
    )
    assert (
        json.loads(mock_request.call_args.kwargs["data"])["data"]["relationships"]
        == expected_relationships
    )
