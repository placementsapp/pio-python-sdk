"""
APIResponse class for handling JSON:API responses with included resources.

This module provides the APIResponse class that wraps API response data,
merges included resources into relationship data, and maintains backward
compatibility by inheriting from list.
"""


class APIResponse(list):
    """
    Wraps API response data and provides access to included resources.

    This class merges included resources into relationship data while maintaining
    backward compatibility by inheriting from list. All standard list operations
    (iteration, indexing, len, isinstance checks) work as expected.

    Attributes:
        included: List of included resource objects from the API response.
        meta: Metadata dictionary from the API response.

    Example:
        >>> response = await pio.campaigns.get(id=123, include=["opportunity"])
        >>> # Access data like a list
        >>> for campaign in response:
        ...     print(campaign['attributes']['name'])
        >>> # Access merged relationship data
        >>> opp = response[0]['relationships']['opportunity']['data']
        >>> print(opp['attributes']['name'])  # Full attributes available
        >>> # Access raw included array
        >>> print(response.included)
    """

    def __init__(self, data, included=None, meta=None):
        """
        Initialize API response.

        Args:
            data: List of resource objects from the API response.
            included: List of included resource objects.
            meta: Metadata from the API response.
        """
        self.included = included or []
        self.meta = meta or {}

        # Merge included resources into relationship data
        merged_data = self._merge_included(data, self.included)

        # Initialize list with merged data
        if isinstance(merged_data, list):
            super().__init__(merged_data)
        else:
            super().__init__([merged_data] if merged_data else [])

    def _merge_included(self, data, included):
        """
        Merge included resources into their corresponding relationships.

        For each relationship that has a 'data' field with type and id,
        find the matching resource in the included array and merge its
        full attributes and relationships into the relationship data.

        Args:
            data: List of primary resource objects.
            included: List of included resource objects.

        Returns:
            Data with included resources merged into relationships.
        """
        if not included:
            return data

        # Create lookup dict for included resources: {(type, id): resource}
        included_map = {
            (resource.get("type"), resource.get("id")): resource
            for resource in included
        }

        def merge_relationships(obj):
            """Recursively merge included resources into an object's relationships."""
            if not isinstance(obj, dict):
                return obj

            # Process relationships if they exist
            relationships = obj.get("relationships", {})
            for rel_name, rel_data in relationships.items():
                if not isinstance(rel_data, dict):
                    continue

                rel_data_obj = rel_data.get("data")

                if rel_data_obj is None:
                    continue

                # Handle to-one relationships (single object)
                if isinstance(rel_data_obj, dict):
                    key = (rel_data_obj.get("type"), rel_data_obj.get("id"))
                    if key in included_map:
                        # Merge the full included resource
                        merged = {**included_map[key]}
                        # Recursively merge nested relationships
                        merge_relationships(merged)
                        rel_data["data"] = merged

                # Handle to-many relationships (array of objects)
                elif isinstance(rel_data_obj, list):
                    merged_list = []
                    for item in rel_data_obj:
                        if not isinstance(item, dict):
                            merged_list.append(item)
                            continue
                        key = (item.get("type"), item.get("id"))
                        if key in included_map:
                            merged = {**included_map[key]}
                            merge_relationships(merged)
                            merged_list.append(merged)
                        else:
                            merged_list.append(item)
                    rel_data["data"] = merged_list

            return obj

        # Process each item in data
        if isinstance(data, list):
            return [merge_relationships(item) for item in data]
        else:
            return merge_relationships(data)

    def __repr__(self):
        """String representation."""
        return (
            f"APIResponse({len(self)} items, "
            f"included={len(self.included)} items, "
            f"meta={list(self.meta.keys()) if self.meta else []})"
        )
