"""
python example/line_item/get_line_item_by_campaign.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --campaign_id 600220
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_line_item_by_campaign(environment: str, token: str, campaign_id: int):
    pio = PlacementsIO(environment=environment, token=token)
    campaign = await pio.line_items.get(campaign=campaign_id)
    print(json.dumps(campaign, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get line item by campaign id.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--campaign_id",
        type=int,
        help="The campaign id to get line item for.",
    )
    args = parser.parse_args()
    asyncio.run(get_line_item_by_campaign(**vars(args)))
