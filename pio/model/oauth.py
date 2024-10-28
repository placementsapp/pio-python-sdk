"""
Models for the PlacementsIO_OAuth
"""

from typing import List, Literal
from pio.model.service import services

service_scopes = [f"{service}_read" for service in services] + [
    f"{service}_write" for service in services
]
ModelScopes = List[Literal[tuple(service_scopes)]]
