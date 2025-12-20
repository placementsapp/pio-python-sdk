"""
Tests for PlacementsIOClient helper methods
"""

from pio.client import PlacementsIOClient


# ============================================================================
# Tests for _fields_values sparse fieldsets
# ============================================================================


def test_fields_values_with_list():
    """Test _fields_values with list format (backwards compatible)"""
    client = PlacementsIOClient()
    result = client._fields_values("campaigns", ["name", "id"])
    assert result == {"fields[campaigns]": "name,id"}


def test_fields_values_with_dict():
    """Test _fields_values with dict format for multiple entity types"""
    client = PlacementsIOClient()
    result = client._fields_values("campaigns", {
        "campaigns": ["name", "ad-server-info"],
        "accounts": ["custom-fields"]
    })
    assert result == {
        "fields[campaigns]": "name,ad-server-info",
        "fields[accounts]": "custom-fields"
    }


def test_fields_values_normalizes_underscores():
    """Test _fields_values normalizes underscores to hyphens"""
    client = PlacementsIOClient()
    result = client._fields_values("line_items", {
        "line_items": ["name"],
        "accounts": ["id"]
    })
    assert result == {
        "fields[line-items]": "name",
        "fields[accounts]": "id"
    }


def test_fields_values_empty():
    """Test _fields_values returns empty dict for empty/None inputs"""
    client = PlacementsIOClient()
    assert client._fields_values("campaigns", None) == {}
    assert client._fields_values("campaigns", []) == {}
    assert client._fields_values("campaigns", {}) == {}
