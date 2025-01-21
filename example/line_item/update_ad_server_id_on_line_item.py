"""
python example/line_item/update_ad_server_id_on_line_item.py \
    --line_item_id 11111 \
    --ad_server_id 'abc-123'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_ad_server_id_on_line_item(
    environment: str,
    token: str,
    line_item_id: int,
    ad_server_id: str,
):
    pio = PlacementsIO(environment=environment, token=token)

    results = await pio.line_items.update(
        resource_ids=[line_item_id],
        attributes={"ad-server-id": ad_server_id},
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the ad server id for line item."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--line_item_id",
        type=int,
        help="The line item id to update",
    )
    parser.add_argument(
        "--ad_server_id",
        type=str,
        help="The ad server id to set for the line item.",
    )
    args = parser.parse_args()
    asyncio.run(update_ad_server_id_on_line_item(**vars(args)))
