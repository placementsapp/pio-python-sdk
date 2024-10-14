"""
python example/line_item/update_start_and_end_date_of_line_items.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --attributes '{
    "3701454": {"start-date": "2024-10-07 00:00:00", "end-date": "2024-12-31 11:59:59"}
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


async def update_start_and_end_date_of_line_items(
    environment: str, token: str, attributes: dict
):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_line_item_settings(line_item_id):
        return attributes[line_item_id]

    results = await pio.line_items.update(
        attributes.keys(),
        attributes=update_line_item_settings,
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the start and end date of line items."
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
        help="A dictionary of line item IDs to dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_start_and_end_date_of_line_items(**vars(args)))
