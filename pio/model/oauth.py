"""
Models for the PlacementsIO_OAuth
"""

from typing import List, Literal

rw_services = [
    "accounts",
    "campaigns",
    "contacts",
    "creatives",
    "custom_fields",
    "external_users",
    "groups",
    "line_items",
    "line_item_creative_associations",
    "opportunities",
    "opportunity_line_items",
    "packages",
    "products",
    "product_rates",
    "rate_cards",
    "reports",
    "users",
]
service_scopes = [f"{service}_read" for service in rw_services] + [
    f"{service}_write" for service in rw_services
]
ModelScopes = List[Literal[tuple(service_scopes)]]
