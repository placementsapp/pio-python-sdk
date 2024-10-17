import pytest
from unittest.mock import Mock
import httpx


from pio import PlacementsIO


@pytest.mark.asyncio
async def test_get_accounts():
    pio = PlacementsIO(environment="staging", token="foo")
    accounts = pio.accounts()
    assert accounts == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]


# @pytest.fixture
# def mock_httpx_get(mocker):
#     mock = mocker.patch('httpx.get')
#     return mock

# def test_deposit(mock_httpx_get):
#     # Mock the httpx.get response
#     mock_httpx_get.return_value = Mock(status_code=200, json=lambda: {"balance": 100})

#     account = Account()
#     account.deposit(100)

#     assert account.balance == 100
#     mock_httpx_get.assert_called_once_with('http://example.com/deposit', params={'amount': 100})

# def test_withdraw(mock_httpx_get):
#     # Mock the httpx.get response
#     mock_httpx_get.return_value = Mock(status_code=200, json=lambda: {"balance": 50})

#     account = Account()
#     account.deposit(100)
#     account.withdraw(50)

#     assert account.balance == 50
#     mock_httpx_get.assert_called_once_with('http://example.com/withdraw', params={'amount': 50})

# def test_withdraw_insufficient_funds(mock_httpx_get):
#     # Mock the httpx.get response
#     mock_httpx_get.return_value = Mock(status_code=400, json=lambda: {"error": "Insufficient funds"})

#     account = Account()
#     account.deposit(50)

#     with pytest.raises(ValueError):
#         account.withdraw(100)

#     mock_httpx_get.assert_called_once_with('http://example.com/withdraw', params={'amount': 100})
