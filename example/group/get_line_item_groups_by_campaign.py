"""
python example/campaign/get_line_item_groups_by_campaign.py \
    --campaign_id 123
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_line_item_groups_by_campaign(
    environment: str, token: str, campaign_id: int
):
    pio = PlacementsIO(environment=environment, token=token)
    campaign = await pio.groups.get(campaign=campaign_id)
    print(json.dumps(campaign, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get line item groups by campaign id.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--campaign_id",
        type=int,
        help="The campaign id to get line item groups for.",
    )
    args = parser.parse_args()
    asyncio.run(get_line_item_groups_by_campaign(**vars(args)))
