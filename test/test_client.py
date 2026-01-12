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


# ============================================================================
# Tests for _merge_includes_into_fields
# ============================================================================


def test_merge_includes_into_fields_list():
    """Test merging includes into fields when fields is a list."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="campaigns",
        includes=["advertiser", "line-items"],
        fields=["name"]
    )

    assert "name" in result
    assert "advertiser" in result
    assert "line-items" in result


def test_merge_includes_into_fields_list_no_duplicates():
    """Test that includes already in fields aren't duplicated."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="campaigns",
        includes=["advertiser"],
        fields=["name", "advertiser"]  # advertiser already present
    )

    assert result.count("advertiser") == 1


def test_merge_includes_into_fields_dict():
    """Test merging includes into fields when fields is a dict."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="campaigns",
        includes=["advertiser"],
        fields={"campaigns": ["name"], "accounts": ["custom-fields"]}
    )

    # Should add to primary service
    assert "advertiser" in result["campaigns"]
    # Should NOT add to other resource types
    assert "advertiser" not in result["accounts"]


def test_merge_includes_into_fields_none_includes():
    """Test that None includes returns fields unchanged."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="campaigns",
        includes=None,
        fields=["name"]
    )

    assert result == ["name"]


def test_merge_includes_into_fields_none_fields():
    """Test that None fields returns None (no sparse fieldsets)."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="campaigns",
        includes=["advertiser"],
        fields=None
    )

    assert result is None


def test_merge_includes_into_fields_underscore_service():
    """Test handling of underscored service names like line_items."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="line_items",
        includes=["campaign"],
        fields={"line-items": ["name"]}
    )

    assert "campaign" in result["line-items"]


def test_merge_includes_into_fields_dict_primary_not_specified():
    """Test that when dict fields doesn't include primary service, nothing is added."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="campaigns",
        includes=["advertiser"],
        fields={"accounts": ["custom-fields"]}  # no campaigns key
    )

    # Should return unchanged
    assert result == {"accounts": ["custom-fields"]}
    assert "campaigns" not in result


# ============================================================================
# Tests for nested includes in _merge_includes_into_fields
# ============================================================================


def test_merge_includes_nested_extracts_top_level_list():
    """Test that nested includes extract top-level relationship for list fields."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="line-items",
        includes=["campaign.advertiser"],
        fields=["name"]
    )

    # Should add "campaign" (top-level) not "campaign.advertiser"
    assert "name" in result
    assert "campaign" in result
    assert "campaign.advertiser" not in result


def test_merge_includes_nested_extracts_top_level_dict():
    """Test that nested includes extract top-level relationship for dict fields."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="line-items",
        includes=["campaign.advertiser"],
        fields={"line-items": ["name"]}
    )

    # Should add "campaign" (top-level) not "campaign.advertiser"
    assert "name" in result["line-items"]
    assert "campaign" in result["line-items"]
    assert "campaign.advertiser" not in result["line-items"]


def test_merge_includes_deeply_nested():
    """Test that deeply nested includes (3+ levels) extract top-level only."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="line-items",
        includes=["campaign.advertiser.contacts"],
        fields=["name"]
    )

    # Should only add "campaign" (top-level)
    assert "campaign" in result
    assert "advertiser" not in result
    assert "contacts" not in result


def test_merge_includes_mixed_simple_and_nested():
    """Test mixed simple and nested includes."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="line-items",
        includes=["product", "campaign.advertiser"],
        fields=["name"]
    )

    # Should add both "product" and "campaign"
    assert "product" in result
    assert "campaign" in result
    assert "campaign.advertiser" not in result


def test_merge_includes_nested_deduplication():
    """Test that duplicate top-level includes are deduplicated."""
    client = PlacementsIOClient()

    result = client._merge_includes_into_fields(
        service="line-items",
        includes=["campaign", "campaign.advertiser", "campaign.opportunity"],
        fields=["name"]
    )

    # Should only have "campaign" once
    assert result.count("campaign") == 1
