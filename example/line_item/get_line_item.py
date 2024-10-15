"""
python example/line_item/get_line_item.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --line_item_id 7059899
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_line_item(environment: str, token: str, line_item_id: int):
    pio = PlacementsIO(environment=environment, token=token)
    line_item = await pio.line_items.get(id=line_item_id)
    print(json.dumps(line_item, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get line item information.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--line_item_id",
        type=int,
        help="The line item id to get.",
    )
    args = parser.parse_args()
    asyncio.run(get_line_item(**vars(args)))
