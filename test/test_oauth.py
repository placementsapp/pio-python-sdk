"""
Tests for the GET method of the PlacementsIO class
"""

import re
import json
import pytest
import httpx
from unittest.mock import patch
from pytest_httpx import HTTPXMock
from pio import PlacementsIO_OAuth
from pio.model.service import services
from pio.error.api_error import APIError

# API_SERVICES = [_ for _ in services if _ != "reports"]
URL_REGEX = r"https://api-staging\.placements\.io/v1/(\w+)(\?.*)?"


@pytest.fixture(autouse=True)
def mock_get(httpx_mock: HTTPXMock):
    """
    Mocks successful GET request
    """
    with open("test/data/get/accounts.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="GET",
            url=re.compile(URL_REGEX),
            json=json.load(response),
            status_code=400,
        )


@pytest.fixture(autouse=True)
def mock_oauth_post(httpx_mock: HTTPXMock):
    """
    Mocks successful GET request
    """
    with open("test/data/post/oauth.json", encoding="utf-8") as response:
        httpx_mock.add_response(
            method="POST",
            url="https://api-staging.placements.io/oauth/token",
            json=json.load(response),
            status_code=200,
        )


@patch("pio.oauth.OAUTH_RESPONSE")
@patch("webbrowser.open", return_value=True)
@patch("socketserver.TCPServer")
@pytest.mark.asyncio
async def test_oauth_authentication(mock_tcp_server, mock_webbrowser_open, mock_oauth):
    mock_oauth.return_value = True
    mock_webbrowser_open.return_value = True
    mock_httpd = mock_tcp_server.return_value.__enter__.return_value
    mock_httpd.handle_request.side_effect = lambda: ()

    pio = PlacementsIO_OAuth(
        environment="staging", application_id="abc123", client_secret="abc123"
    )
    accounts = await pio.accounts.get()
    assert accounts
