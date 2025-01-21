"""
python example/product/get_product_cogs.py
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


async def get_product_cogs(environment: str, token: str):
    pio = PlacementsIO(environment=environment, token=token)
    products = await pio.products.get(fields=["name", "cost-of-goods-sold"])
    cogs = []
    for product in products:
        for cogs_setting in (
            product.get("attributes", {}).get("cost-of-goods-sold", []) or []
        ):
            cogs.append(
                {
                    "product_id": product["id"],
                    "product_name": product["attributes"]["name"],
                    **cogs_setting,
                }
            )
    print(json.dumps(cogs, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get COGS for products.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    args = parser.parse_args()
    asyncio.run(get_product_cogs(**vars(args)))
