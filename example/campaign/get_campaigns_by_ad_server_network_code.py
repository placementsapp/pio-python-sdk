"""
python example/campaign/get_campaigns_by_ad_server_network_code.py \
    --network_code 11624
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_campaign_by_id(environment: str, token: str, network_code: int):
    pio = PlacementsIO(environment=environment, token=token)
    campaign = await pio.campaigns.get(ad_server_network_code=network_code)
    print(json.dumps(campaign, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get campaigns by ad server network code.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--network_code",
        type=int,
        help="The ad server network code to get campaigns by",
    )
    args = parser.parse_args()
    asyncio.run(get_campaign_by_id(**vars(args)))
