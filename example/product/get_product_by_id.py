"""
python example/product/get_product_by_id.py \
    --product_id 183951
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


async def get_product_by_id(environment: str, token: str, product_id: int):
    pio = PlacementsIO(environment=environment, token=token)
    product = await pio.products.get(id=product_id)
    print(json.dumps(product, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get product by id.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--product_id",
        type=int,
        help="The product id to get",
    )
    args = parser.parse_args()
    asyncio.run(get_product_by_id(**vars(args)))
