"""
python example/creative/update_creative_details.py \
    --attributes '{
    "15700": {"width": "640", "height": "480"}
}'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_creative_details(environment: str, token: str, attributes: dict):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_creative_settings(creative_id):
        return attributes[creative_id]

    results = await pio.creatives.update(
        attributes.keys(),
        attributes=update_creative_settings,
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update the attributes of creatives.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of creative IDs with dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_creative_details(**vars(args)))
