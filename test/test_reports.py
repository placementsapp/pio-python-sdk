"""
Tests for the UPDATE method of the PlacementsIO class
"""

import re
import json
import pytest
import httpx
from pytest_httpx import HTTPXMock
from pio import PlacementsIO

URL_REGEX = r"https://api-staging\.placements\.io/v1/(\w+)(\?.*)?"


@pytest.fixture()
def mock_create_success(httpx_mock: HTTPXMock):
    """
    Mocks a successful CREATE request
    """

    def custom_response(request):
        match = re.match(URL_REGEX, str(request.url))
        if not match:
            raise ValueError(f"Test URL {request.url} does not match regex {URL_REGEX}")

        with open(f"test/data/post/reports.json", encoding="utf-8") as response:
            return httpx.Response(status_code=200, json=json.load(response))

    httpx_mock.add_callback(custom_response)


@pytest.fixture()
def mock_read_completed(httpx_mock: HTTPXMock):
    """
    Mocks a successful CREATE request
    """

    def custom_response(request):
        match = re.match(URL_REGEX, str(request.url))
        if not match:
            raise ValueError(f"Test URL {request.url} does not match regex {URL_REGEX}")

        with open(f"test/data/get/reports.json", encoding="utf-8") as response:
            return httpx.Response(status_code=200, json=json.load(response))

    httpx_mock.add_callback(custom_response)

@pytest.fixture()
def mock_get_report_csv(httpx_mock: HTTPXMock):
    """
    Mocks successful GET request
    """
    with open("test/data/get/report.csv", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="GET",
            url="https://example.com/report.csv",
            content=response.read(),
            status_code=200,
        )

@pytest.mark.asyncio
async def test_create_report_no_parameters(mock_create_success):
    """Tests a successful update request"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.reports.create()
    print(api_response)
    assert api_response
    assert isinstance(api_response, int)


@pytest.mark.asyncio
async def test_get_completed_report(mock_read_completed):
    """Tests a successful update request"""
    pio = PlacementsIO(environment="staging", token="foo")
    api_response = await pio.reports.get(4)
    print(api_response)
    assert api_response
    assert isinstance(api_response, dict)
    assert api_response.get("attributes") is not None


@pytest.mark.asyncio
async def test_get_completed_report_data(mock_get_report_csv, mock_read_completed):
    """Tests a successful update request"""
    pio = PlacementsIO(environment="staging", token="foo")
    data = await pio.reports.data(4)
    print(data)
    assert len(data) == 5

    # Test matching of columns/rows to dict
    for row in data:
        assert row["A"].strip("A") == row["B"].strip("B")
