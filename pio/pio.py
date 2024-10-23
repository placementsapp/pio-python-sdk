"""
Placements.io API client library
"""

import os
import logging
from typing import Unpack, Union
from pio.client import PlacementsIOClient
from pio.utility.environments import API
from pio.model.get import (
    ModelFilterDefaults,
    ModelFilterAccount,
    ModelFilterCampaign,
    ModelFilterContact,
    ModelFilterCreative,
    ModelFilterCustomField,
    ModelFilterGroup,
    ModelFilterLineItem,
    ModelFilterOpportunity,
    ModelFilterOpportunityLineItem,
    ModelFilterPackage,
    ModelFilterProduct,
    ModelFilterProductRate,
    ModelFilterRateCard,
    ModelFilterReport,
    ModelFilterUser,
)


class PlacementsIO:
    """
    Placements.io API client library
    """

    def __init__(self, environment: str = "staging", token: str = None):
        self.base_url = API[environment]
        self.token = (
            token
            or os.getenv(f"PLACEMENTS_IO_API_TOKEN_{environment.upper()}")
            or os.getenv("PLACEMENTS_IO_API_TOKEN")
        )
        self.logger = logging.getLogger("pio")
        self.settings = {
            "base_url": self.base_url,
            "token": self.token,
        }

    def relationship(self, relationship_url: str):
        """
        Returns a Service class from a relationship URL provided for a previous API call
        """
        return self.Service(
            **{
                "base_url": self.base_url,
                "token": self.token,
                "service": relationship_url.replace(self.base_url, ""),
                "model": {"get": ModelFilterDefaults},
            }
        )

    class Service(PlacementsIOClient):
        """
        Class for interacting with API Services
        """

        def __init__(self, token, base_url, service, model, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.token = token
            self.base_url = base_url
            self.service = service
            self.model = model

        async def get(
            self, include: list = None, **args: Unpack[ModelFilterAccount]
        ) -> list:
            """
            Get existing resources within the service
            """
            return await self.client(
                service=self.service, includes=include, filters=args
            )

        async def update(
            self,
            resource_ids: list,
            attributes: Union[callable, dict] = None,
            relationships: Union[callable, dict] = None,
        ) -> dict:
            """
            Update existing resources within the service
            """
            return await self.client_update(
                service=self.service,
                resource_ids=resource_ids,
                attributes=attributes,
                relationships=relationships,
            )

        async def create(
            self,
            objects: list[dict],
        ) -> dict:
            """
            Create new resources within the service
            """
            return await self.client_create(
                service=self.service,
                objects=objects,
            )

    async def oauth2(self, client_id: str, redirect_url: str) -> Service:
        """
        Returns an OAuth2 Service object for use in interacting with the API
        """
        return await self.Service(
            **self.settings, service="oauth/authorize", model={}
        ).create(
            [
                {
                    "client_id": client_id,
                    "redirect_url": redirect_url,
                    "response_type": "code",
                }
            ]
        )

    @property
    def accounts(self) -> Service:
        """
        Returns an Accounts Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="accounts", model={"get": ModelFilterAccount}
        )

    @property
    def campaigns(self) -> Service:
        """
        Returns a Campaigns Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="campaigns", model={"get": ModelFilterCampaign}
        )

    @property
    def contacts(self) -> Service:
        """
        Returns a Contacts Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="contacts", model={"get": ModelFilterContact}
        )

    @property
    def creatives(self) -> Service:
        """
        Returns a Creatives Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="creatives", model={"get": ModelFilterCreative}
        )

    @property
    def custom_fields(self) -> Service:
        """
        Returns a Custom Fields Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings,
            service="custom_fields",
            model={"get": ModelFilterCustomField},
        )

    @property
    def groups(self) -> Service:
        """
        Returns a Groups Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="groups", model={"get": ModelFilterGroup}
        )

    @property
    def line_items(self) -> Service:
        """
        Returns a Line Items Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="line_items", model={"get": ModelFilterLineItem}
        )

    @property
    def opportunities(self) -> Service:
        """
        Returns an Opportunities Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings,
            service="opportunities",
            model={"get": ModelFilterOpportunity},
        )

    @property
    def opportunity_line_items(self) -> Service:
        """
        Returns an Opportunity Line Items Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings,
            service="opportunity_line_items",
            model={"get": ModelFilterOpportunityLineItem},
        )

    @property
    def packages(self) -> Service:
        """
        Returns a Packages Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="packages", model={"get": ModelFilterPackage}
        )

    @property
    def products(self) -> Service:
        """
        Returns a Products Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="products", model={"get": ModelFilterProduct}
        )

    @property
    def product_rates(self) -> Service:
        """
        Returns a Product Rates Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings,
            service="product_rates",
            model={"get": ModelFilterProductRate},
        )

    @property
    def rate_cards(self) -> Service:
        """
        Returns a Rate Cards Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings,
            service="rate_cards",
            model={"get": ModelFilterRateCard},
        )

    @property
    def reports(self) -> Service:
        """
        Returns a Reports Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="reports", model={"get": ModelFilterReport}
        )

    @property
    def users(self) -> Service:
        """
        Returns a Users Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings, service="users", model={"get": ModelFilterUser}
        )
