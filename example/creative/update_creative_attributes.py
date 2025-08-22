"""
python example/creative/update_creative_attributes.py \
    --push_to_ad_server True \
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


async def update_creative_attributes(
    environment: str, token: str, push_to_ad_server: bool, attributes: dict
):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_creative_settings(creative_id):
        return attributes[creative_id]

    results = await pio.creatives.update(
        attributes.keys(),
        attributes=update_creative_settings,
        params={"skip_push_to_ad_server": (not push_to_ad_server)},
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
        "--push_to_ad_server",
        type=lambda v: v.lower() != "false",
        default=True,
        help="Whether to push the changes to the ad server after update.",
    )
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of creative IDs with dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_creative_attributes(**vars(args)))
