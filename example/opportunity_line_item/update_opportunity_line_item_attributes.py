"""
python example/opportunity_line_item/update_opportunity_line_item_attributes.py \
    --push_to_crm True \
    --attributes '{
    "1136338": {"cost-per-unit": 12.3456}
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


async def update_opportunity_line_item_attributes(
    environment: str,
    token: str,
    attributes: dict, push_to_crm: bool = True
):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_opportunity_line_item_settings(line_item_id):
        return attributes[line_item_id]

    results = await pio.opportunity_line_items.update(
        attributes.keys(),
        attributes=update_opportunity_line_item_settings,
        params={"skip_push_to_crm": (not push_to_crm)},
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get information on a rate card.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--push_to_crm",
        type=bool,
        help="Whether to push the changes to the CRM after update.",
        default=True,
    )
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of opportunity line item IDs to dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_opportunity_line_item_attributes(**vars(args)))
