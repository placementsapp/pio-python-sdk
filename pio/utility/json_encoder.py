"""
JSON Encoder Utility
"""

import json
import datetime


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle objects like datetime before they are sent to the API.
    """

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)  # pragma: no cover
