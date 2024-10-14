"""
python example/opportunity_line_item/get_opportunity_line_item_by_name.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --opportunity_line_item_name 'Opportunity Line'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_opportunity_line_item_by_name(
    environment: str, token: str, opportunity_line_item_name: str
):
    pio = PlacementsIO(environment=environment, token=token)
    result = await pio.opportunity_line_items.get(name=opportunity_line_item_name)
    print(json.dumps(result, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get information on opportunity line items by name."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--opportunity_line_item_name",
        type=str,
        help="The name to search for.",
    )
    args = parser.parse_args()
    asyncio.run(get_opportunity_line_item_by_name(**vars(args)))
