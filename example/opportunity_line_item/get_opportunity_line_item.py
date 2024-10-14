"""
python example/opportunity_line_item/get_opportunity_line_item.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --opportunity_line_item 1136338
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_opportunity_line_item(
    environment: str, token: str, opportunity_line_item: int
):
    pio = PlacementsIO(environment=environment, token=token)
    result = await pio.opportunity_line_items.get(id=opportunity_line_item)
    print(json.dumps(result, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get information on an opportunity line item."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--opportunity_line_item",
        type=int,
        help="The opportunity line item id",
    )
    args = parser.parse_args()
    asyncio.run(get_opportunity_line_item(**vars(args)))
