"""
python example/campaign/get_recently_modified_campaigns.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --modified-since "2024-10-01 00:00:00"
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import datetime
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_recently_modified_campaigns(
    environment: str, token: str, modified_since: datetime.datetime
):
    pio = PlacementsIO(environment=environment, token=token)
    campaign = await pio.campaigns.get(modified_since=modified_since)
    print(json.dumps(campaign, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get recently modified campaigns.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--modified-since",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S"),
        help="The datetime to filter campaign modified since (format: 'YYYY-MM-DD HH:MM:SS').",
    )
    args = parser.parse_args()
    asyncio.run(get_recently_modified_campaigns(**vars(args)))
