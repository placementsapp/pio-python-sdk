"""
python example/campaign/update_start_and_end_date_of_campaigns.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --attributes '{
    "600220": {"start-date": "2024-10-07 00:00:00", "end-date": "2024-12-31 11:59:59"}
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


async def update_start_and_end_date_of_campaigns(
    environment: str, token: str, attributes: dict
):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_campaign_settings(campaign_id):
        return attributes[campaign_id]

    results = await pio.campaigns.update(
        attributes.keys(),
        attributes=update_campaign_settings,
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the start and end date of campaigns."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of campaign IDs to dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_start_and_end_date_of_campaigns(**vars(args)))
