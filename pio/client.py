"""
Placements.io Python SDK
Low level code to interact with the Placements.io Python SDK
"""

import logging
import asyncio
import json
from typing import Union
import httpx
from pio.error.api_error import APIError
from pio.utility.json_encoder import JSONEncoder


class PlacementsIOClient:
    """
    Placements.io Python SDK
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

    def headers(self, method, service, is_retry) -> dict:
        """
        Returns standardized headers for the API request.
        """
        token = self.token
        if callable(self.token):
            token = self.token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
            "User-Agent": f"PlacementsIO Python SDK/{self._version}",
            "x-metadata": json.dumps(
                {"method": method, "service": service.split("/")[0], "is_retry": is_retry}
            ),
        }

    async def client_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        resource: str,
        request: dict,
        is_retry: bool = False,
    ) -> httpx.Response:
        client_method = getattr(client, method)
        request = {
            "url": resource,
            "headers": self.headers(method, resource, is_retry),
            **request,
        }
        if request.get("data") and not isinstance(request["data"], str):
            request["data"] = json.dumps(request["data"], default=str, cls=JSONEncoder)
        response = await client_method(**request)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            self.logger.warning(
                "Rate limit reached. Waiting %s seconds before retrying...",
                retry_after,
            )
            await asyncio.sleep(retry_after)
            return await self.client_request(
                client, method, resource, request, is_retry=True
            )
        return response

    async def client(
        self,
        service: str,
        param: dict = None,
        filters: dict = None,
        includes: list = None,
        fields: list = None,
    ) -> list:
        """
        Get existing resources within the service
        """
        # TODO: Need to have a way to call multiple IDs at the same time
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60) as client:

            param = param or {}
            param.update(self.pagination())
            param.update(self._filter_values(filters))
            param.update(self._list_values("include", includes))
            param.update(self._list_values(f"fields[{service}]", fields))
            self.logger.info("Fetching data from %s", service)
            response = await self.client_request(
                client, "get", service, {"params": param}
            )
            data = response.json()
            errors = data.get("errors", [])
            if errors:
                raise APIError(errors)
            results = data.get("data", [])
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
                    self.client_request(
                        client, "get", service, {"params": paginated_param}
                    )
                )
            responses = await asyncio.gather(*tasks)
            for response in responses:
                data = response.json()
                data = data.get("data", [])
                results.extend(data)

            return results

    async def resource(
        self,
        service: str,
        resource_id: int,
    ) -> dict:
        """
        Get a single existing resource within the service
        """

        # Follow_redirects is set to True to facilitate report downloads
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=60, follow_redirects=True
        ) as client:
            path = f"{service}/{resource_id}"
            self.logger.info("Fetching data from %s %s", service, resource_id)
            response = await self.client_request(client, "get", path, {})
            data = response.json()
            errors = data.get("errors", [])
            if errors:
                raise APIError(errors)
            results = data.get("data", {})
            return results

    async def client_update(
        self,
        service: str,
        resource_ids: list,
        attributes: Union[callable, dict] = None,
        relationships: Union[callable, dict] = None,
        params: dict = None,
    ) -> dict:
        """
        Update existing resources within the service
        """
        if not attributes and not relationships:
            raise ValueError(
                "Must provide either attributes or relationships to update."
            )

        async def get_responses(resource_ids: list) -> dict:

            async def make_multiple_requests(resource_ids: int) -> dict:

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
                            "Updating %s %s",
                            url,
                            params,
                        )
                        self.logger.debug(
                            "Payload: %s",
                            json.dumps(payload, indent=4, default=str, cls=JSONEncoder),
                        )
                        tasks.append(
                            self.client_request(
                                client,
                                "patch",
                                url,
                                {"data": payload, "params": params},
                            )
                        )
                    return await asyncio.gather(*tasks)

            responses_dict = {}
            responses = await make_multiple_requests(resource_ids)
            responses_dict.update(dict(zip(resource_ids, responses)))
            return responses_dict

        # Split resource_ids into chunks of 100
        chunk_size = 100
        raw_responses = {}
        if isinstance(resource_ids, {}.keys().__class__):
            resource_ids = list(resource_ids)
        for index in range(0, len(resource_ids), chunk_size):
            chunk = resource_ids[index : index + chunk_size]
            chunk_responses = await get_responses(chunk)
            raw_responses.update(chunk_responses)

        expanded_responses = [
            (
                response.json().get(
                    "data", {**response.json(), "links": {"self": response.request.url}}
                )
                if response.content
                else {
                    "errors": [
                        {
                            "title": "No data",
                            "detail": "No data was returned in the API response",
                        }
                    ],
                    "links": {"self": response.request.url},
                }
            )
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

            async def make_multiple_requests(objects) -> list:
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
                            self.client_request(
                                client, "post", service, {"data": payload}
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
                responses = await make_multiple_requests(objects)

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

    def _list_values(self, key: str, relationships: list = None) -> dict:
        params = {}
        if relationships:
            params = {key: ",".join(relationships)}
        return params
