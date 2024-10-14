import os
import httpx
import logging
import asyncio
import json
from typing import Unpack, Union
from pio._model import *

# TODO: look into HTTPX transports for handling 429 errors - https://www.python-httpx.org/advanced/transports/#http-transport


class APIError(Exception):
    pass


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return super().default(obj)


class PlacementsIOClient:

    def __init__(self):
        self.logger = logging.getLogger("pio")

    def pagination(self, page_number: int = 1) -> dict:
        return {
            "page[number]": page_number,
            "page[size]": 10,
        }

    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/vnd.api+json",
            "User-Agent": f"PlacementsIO Python Client/{os.environ["PLACEMENTS_IO_CLIENT_VERSION"]}",
            "x-metadata": json.dumps({"release": "alpha"}),
        }

    async def client(
        self,
        service: str,
        param: dict = None,
        filter: dict = None,
        include: list = None,
    ) -> list:
        # TODO: Need to have a way to call multiple IDs at the same time
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:

            async def make_request(service_name: str, service_param: dict) -> dict:
                return await client.get(
                    headers=self.headers(),
                    url=service_name,
                    params=service_param,
                )

            param = param or {}
            param.update(self.pagination())
            param.update(self._filter_values(filter))
            param.update(self._include_values(include))
            self.logger.info(f"Fetching data from {service}")
            response = await make_request(service, param)
            data = response.json()
            self.logger.debug(json.dumps(data, indent=4, default=str, cls=JSONEncoder))
            errors = data.get("errors", [])
            if errors:
                raise APIError(errors)
            results = data.get("data", {})
            meta = data.get("meta", {})
            page_count = meta.get("page-count", 0)
            if page_count > 1:
                self.logger.info(f"Paginating data from {service} [{page_count} Pages]")

            tasks = []
            for page_number in range(2, page_count + 1):
                paginated_param = param.copy()
                paginated_param.update(self.pagination(page_number))
                tasks.append(
                    make_request(service_name=service, service_param=paginated_param)
                )
            responses = await asyncio.gather(*tasks)
            for response in responses:
                data = response.json()
                data = data.get("data", [])
                results.extend(data)

            return results

    async def client_update(
        self,
        service: str,
        resource_ids: list,
        attributes: Union[callable, dict] = None,
        relationships: Union[callable, dict] = None,
    ) -> dict:
        if not attributes and not relationships:
            raise ValueError(
                "Must provide either attributes or relationships to update."
            )

        async def get_responses(resource_ids: list) -> dict:

            async def make_request(resource_ids: int) -> dict:
                async with httpx.AsyncClient(
                    base_url=self.base_url, timeout=60
                ) as client:
                    tasks = []
                    for resource_id in resource_ids:
                        url = f"{service}/{resource_id}"

                        attributes_payload = {}
                        if isinstance(attributes, dict):
                            attributes_payload = {"attributes": attributes}
                        elif callable(attributes):
                            attributes_payload = {
                                "attributes": await attributes(resource_id)
                            }

                        relationships_payload = {}
                        if isinstance(relationships, dict):
                            relationships_payload = {"relationships": relationships}
                        elif callable(relationships):
                            relationships_payload = {
                                "relationships": await relationships(resource_id)
                            }

                        payload = {
                            "data": {
                                "id": resource_id,
                                "type": service,
                                **attributes_payload,
                                **relationships_payload,
                            }
                        }
                        self.logger.info(
                            f"Updating {url}",
                            json.dumps(payload, indent=4, default=str, cls=JSONEncoder),
                        )
                        tasks.append(
                            client.patch(
                                url,
                                headers=self.headers(),
                                data=json.dumps(payload, default=str, cls=JSONEncoder),
                            )
                        )
                    return await asyncio.gather(*tasks)

            attempts = 0
            retry_after = 60
            responses_dict = {}
            while resource_ids:
                # self.logger.info(resource_ids)
                if attempts:
                    self.logger.warning(
                        f"{len(resource_ids)} Resource IDs remaining..."
                    )
                    self.logger.warning(
                        f"Waiting {retry_after} seconds before retrying..."
                    )
                    await asyncio.sleep(retry_after)
                responses = await make_request(resource_ids)
                responses_dict.update(dict(zip(resource_ids, responses)))

                # Now look for 429 responses to retry, or update the response with JSON
                resource_ids = []
                for resource_id, response in responses_dict.items():
                    if response.status_code == 429:
                        resource_ids.append(resource_id)
                    else:
                        responses_dict[resource_id] = response
                attempts += 1
            return responses_dict

        raw_responses = await get_responses(resource_ids)
        expanded_responses = [
            response.json().get("data", response.json())
            for response in raw_responses.values()
        ]
        return expanded_responses

    async def client_create(
        self,
        service: str,
        objects: list[dict],
    ) -> dict:

        async def get_responses(objects: list) -> list:

            class JSONEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, datetime):
                        return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    return super().default(obj)

            async def make_request(objects) -> list:
                async with httpx.AsyncClient(
                    base_url=self.base_url, timeout=60
                ) as client:
                    tasks = []
                    for resources in objects:
                        attributes = resources.get("attributes")
                        relationships = resources.get("relationships")

                        attributes_payload = {}
                        if isinstance(attributes, dict):
                            attributes_payload = {"attributes": attributes}

                        relationships_payload = {}
                        if isinstance(relationships, dict):
                            relationships_payload = {"relationships": relationships}

                        payload = {
                            "data": {
                                "type": service,
                                **attributes_payload,
                                **relationships_payload,
                            }
                        }
                        tasks.append(
                            client.post(
                                service,
                                headers=self.headers(),
                                data=json.dumps(payload, default=str, cls=JSONEncoder),
                            )
                        )
                    return await asyncio.gather(*tasks)

            attempts = 0
            retry_after = 60
            responses_final = []
            while len(objects) != len(responses_final):
                self.logger.info(objects)
                if attempts:
                    self.logger.warning(f"{len(objects)} Resources remaining...")
                    self.logger.warning(
                        f"Waiting {retry_after} seconds before retrying..."
                    )
                    await asyncio.sleep(retry_after)
                responses = await make_request(objects)

                # Now look for 429 responses to retry, or update the response with JSON
                for response in responses:
                    if response.status_code != 429:
                        responses_final.append(response)
                attempts += 1
            return responses_final

        raw_responses = await get_responses(objects)
        expanded_responses = [
            response.json().get("data", response.json()) for response in raw_responses
        ]
        return expanded_responses

    def _filter_values(self, params: dict = None) -> str:
        params = params or {}
        return {f"filter[{key}]": value for key, value in params.items()}

    def _include_values(self, relationships: dict = None) -> str:
        return {"include": _ for _ in relationships or []}


class PlacementsIO:
    def __init__(self, environment: str = "staging", token: str = None):
        environments = {
            "production": "https://api.placements.io/v1/",
            "edge": "https://edge-api.placements.io/v1/",
            "staging": "https://api-staging.placements.io/v1/",
        }
        self.base_url = environments[environment]
        self.token = (
            token
            or os.getenv(f"PLACEMENTS_IO_API_TOKEN_{environment.upper()}")
            or os.getenv(f"PLACEMENTS_IO_API_TOKEN")
        )
        self.logger = logging.getLogger("pio")
        self.settings = {
            "base_url": self.base_url,
            "token": self.token,
        }

    def relationship(self, relationship_url: str):
        return self.Service(
            **{
                "base_url": self.base_url,
                "token": self.token,
                "base_url": self.base_url,
                "service": relationship_url.replace(self.base_url, ""),
                "model": {"get": ModelFilterDefaults},
            }
        )

    class Service(PlacementsIOClient):
        def __init__(self, token, base_url, service, model, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.token = token
            self.base_url = base_url
            self.service = service
            self.model = model

        async def get(
            self, include: list = None, **args: Unpack[ModelFilterAccount]
        ) -> list:
            return await self.client(service=self.service, include=include, filter=args)

        async def update(
            self,
            resource_ids: list,
            attributes: Union[callable, dict] = None,
            relationships: Union[callable, dict] = None,
        ) -> dict:
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
            return await self.client_create(
                service=self.service,
                objects=objects,
            )

    @property
    def accounts(self) -> Service:
        return self.Service(
            **self.settings, service="accounts", model={"get": ModelFilterAccount}
        )

    @property
    def campaigns(self) -> Service:
        return self.Service(
            **self.settings, service="campaigns", model={"get": ModelFilterCampaign}
        )

    @property
    def contacts(self) -> Service:
        return self.Service(
            **self.settings, service="contacts", model={"get": ModelFilterContact}
        )

    @property
    def creatives(self) -> Service:
        return self.Service(
            **self.settings, service="creatives", model={"get": ModelFilterCreative}
        )

    @property
    def custom_fields(self) -> Service:
        return self.Service(
            **self.settings,
            service="custom_fields",
            model={"get": ModelFilterCustomField},
        )

    @property
    def groups(self) -> Service:
        return self.Service(
            **self.settings, service="groups", model={"get": ModelFilterGroup}
        )

    @property
    def line_items(self) -> Service:
        return self.Service(
            **self.settings, service="line_items", model={"get": ModelFilterLineItem}
        )

    @property
    def opportunities(self) -> Service:
        return self.Service(
            **self.settings,
            service="opportunities",
            model={"get": ModelFilterOpportunity},
        )

    @property
    def opportunity_line_items(self) -> Service:
        return self.Service(
            **self.settings,
            service="opportunity_line_items",
            model={"get": ModelFilterOpportunityLineItem},
        )

    @property
    def packages(self) -> Service:
        return self.Service(
            **self.settings, service="packages", model={"get": ModelFilterPackage}
        )

    @property
    def products(self) -> Service:
        return self.Service(
            **self.settings, service="products", model={"get": ModelFilterProduct}
        )

    @property
    def product_rates(self) -> Service:
        return self.Service(
            **self.settings,
            service="product_rates",
            model={"get": ModelFilterProductRate},
        )

    @property
    def rate_cards(self) -> Service:
        return self.Service(
            **self.settings,
            service="rate_cards",
            model={"get": ModelFilterRateCard},
        )

    @property
    def reports(self) -> Service:
        return self.Service(
            **self.settings, service="reports", model={"get": ModelFilterReport}
        )

    @property
    def users(self) -> Service:
        return self.Service(
            **self.settings, service="users", model={"get": ModelFilterUser}
        )
