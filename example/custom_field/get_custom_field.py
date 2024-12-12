"""
python example/custom_field/get_custom_field.py \
    --custom_field_id 3551
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_custom_field(environment: str, token: str, custom_field_id: int):
    pio = PlacementsIO(environment=environment, token=token)
    custom_field = await pio.custom_fields.get(id=custom_field_id)
    print(json.dumps(custom_field, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get custom field information.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--custom_field_id",
        type=int,
        help="The custom field id to get.",
    )
    args = parser.parse_args()
    asyncio.run(get_custom_field(**vars(args)))
