"""
python example/line_item/get_line_item_cogs.py
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


async def get_line_item_cogs(environment: str, token: str):
    pio = PlacementsIO(environment=environment, token=token)
    line_items = await pio.line_items.get(fields=["name", "cost-of-goods-sold"])
    cogs = []
    for line_item in line_items:
        for cogs_setting in (
            line_item.get("attributes", {}).get("cost-of-goods-sold", []) or []
        ):
            cogs.append(
                {
                    "line_item_id": line_item["id"],
                    "line_item_name": line_item["attributes"]["name"],
                    **cogs_setting,
                }
            )
    print(json.dumps(cogs, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get COGS for line items.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    args = parser.parse_args()
    asyncio.run(get_line_item_cogs(**vars(args)))
