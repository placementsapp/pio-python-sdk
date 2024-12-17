"""
Placements.io Python SDK
"""

import os
import logging
import datetime
import csv
import time
from typing import Unpack, Union
from pio.client import PlacementsIOClient
from pio.error.api_error import APIError
from pio.model.environment import API
from pio.model.report import COLUMNS
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
import httpx


class PlacementsIO:
    """
    Placements.io Python SDK
    """

    def __init__(self, environment: str = None, token: str = None):
        environment = (
            environment or os.environ.get(f"PLACEMENTS_IO_ENVIRONMENT") or "staging"
        )
        self.base_url = API.get(environment, environment)
        self.token = (
            token
            or os.environ.get(f"PLACEMENTS_IO_TOKEN_{environment.upper()}")
            or os.environ.get("PLACEMENTS_IO_TOKEN")
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
            self,
            include: list = None,
            fields: list = None,
            params: dict = None,
            **args: Unpack[ModelFilterAccount],
        ) -> list:
            """
            Get existing resources within the service
            """
            return await self.client(
                service=self.service,
                includes=include,
                filters=args,
                fields=fields,
                param=params,
            )

        async def update(
            self,
            resource_ids: list,
            attributes: Union[callable, dict] = None,
            relationships: Union[callable, dict] = None,
            params: dict = None,
        ) -> dict:
            """
            Update existing resources within the service
            """
            return await self.client_update(
                service=self.service,
                resource_ids=resource_ids,
                attributes=attributes,
                relationships=relationships,
                params=params,
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

    class ReportService(Service):
        """
        Class for interacting with API Reports Service
        """

        TODAY_START = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        TODAY_END = datetime.datetime.now(datetime.timezone.utc).replace(
            hour=23, minute=59, second=59, microsecond=999
        )

        async def create(
            self, start_date=TODAY_START, end_date=TODAY_END, columns: list = COLUMNS
        ) -> int:
            """
            Create a new report
            """
            report_creation_request = [
                {
                    "attributes": {
                        "definition": {
                            "start-date": start_date,
                            "end-date": end_date,
                            "columns": columns,
                        }
                    }
                }
            ]
            report_creation = await self.client_create(
                service=self.service, objects=report_creation_request
            )
            report_id = report_creation[0].get("id")
            return report_id

        async def get(self, resource_id: int) -> dict:
            """
            Get existing resources within the service
            """
            return await self.resource(service=self.service, resource_id=resource_id)

        async def data(self, report_id: dict) -> list:
            """
            Returns report data in a list of dictionaries
            """

            report_response = await self.get(report_id)
            status = report_response.get("attributes", {}).get("status")
            while status in ["pending", "in_progress"]:
                self.logger.info(f"Report is currently {status}. Retrying in 5 seconds")
                time.sleep(5)
                report_response = await self.get(report_id)
                status = report_response.get("attributes", {}).get("status")
            if status == "failed":
                raise APIError(
                    report_response.get("attributes", {}).get("error-message")
                )

            download_url = report_response.get("attributes", {}).get("download-url")
            if not download_url:
                raise APIError(
                    "No download report URL found in response. Unable to download report data.",
                    report_response,
                )
            async with httpx.AsyncClient() as data_client:
                async with data_client.stream(
                    "GET", download_url, follow_redirects=True
                ) as response:
                    response.raise_for_status()
                    lines = []
                    async for line in response.aiter_lines():
                        lines.append(line)
                    csv_reader = csv.reader(lines)
                    headers = next(csv_reader)
                    rows = []
                    for row in csv_reader:
                        rows.append(dict(zip(headers, row)))
                    return rows

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
    def external_users(self) -> Service:
        """
        Returns a External Users Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings,
            service="external_users",
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
    def line_item_creative_associations(self) -> Service:
        """
        Returns a Line Item Creative Associations Service object for use in interacting with the API
        """
        return self.Service(
            **self.settings,
            service="line_item_creative_associations",
            model={"get": ModelFilterDefaults},
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
        return self.ReportService(
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
