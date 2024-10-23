"""
Placements.io API client library
Low level code to interact with the Placements.io API
"""

import logging
import asyncio
import json
from typing import Union
import httpx
from pio.error.api_error import APIError
from pio.utility.json_encoder import JSONEncoder

# TODO: look into HTTPX transports for handling 429 errors
#   https://www.python-httpx.org/advanced/transports/#http-transport


class PlacementsIOClient:
    """
    Placements.io API client library
    Low level code to interact with the Placements.io API
    """

    def __init__(self):
        self.logger = logging.getLogger("pio")
        self.base_url = None
        self.token = None

    @property
    def _version(self):
        """
        Returns the version of the client library
        Note: This is locally imported to avoid circular imports
        """
        from pio import __version__  # pylint: disable=import-outside-toplevel

        return __version__

    def pagination(self, page_number: int = 1) -> dict:
        """
        Provides pagination parameters for the API request.
        """
        return {
            "page[number]": page_number,
            "page[size]": 100,
        }

    def headers(self) -> dict:
        """
        Returns standardized headers for the API request.
        """
        token = self.token
        if callable(self.token):
            token = self.token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
            "User-Agent": f"PlacementsIO Python Client/{self._version}",
            "x-metadata": json.dumps({"release": "alpha"}),
        }

    async def client(
        self,
        service: str,
        param: dict = None,
        filters: dict = None,
        includes: list = None,
    ) -> list:
        """
        Get existing resources within the service
        """
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
            param.update(self._filter_values(filters))
            param.update(self._include_values(includes))
            self.logger.info("Fetching data from %s", service)
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
                self.logger.info(
                    "Paginating data from %s [%s Pages]", service, page_count
                )

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
        """
        Update existing resources within the service
        """
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
                            "Updating %s with payload: %s",
                            url,
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
                if attempts:
                    self.logger.warning(
                        "%s Resource IDs remaining...", len(resource_ids)
                    )
                    self.logger.warning(
                        "Waiting %s seconds before retrying...", retry_after
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
        """
        Create new resources within the service
        """

        async def get_responses(objects: list) -> list:

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
                    self.logger.warning("%s Resources remaining...", len(objects))
                    self.logger.warning(
                        "Waiting %s seconds before retrying...", retry_after
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
