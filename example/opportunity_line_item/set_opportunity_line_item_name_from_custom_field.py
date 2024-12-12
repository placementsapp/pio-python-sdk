"""
python example/opportunity_line_item/set_opportunity_line_item_name_from_custom_field.py \
    --opportunity_line_items 1,2,3 \
    --custom_field_name 'FCAP Buy Name'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def set_opportunity_line_item_name_from_custom_field(
    environment: str,
    token: str,
    opportunity_line_items: list[int],
    custom_field_name: str,
):
    pio = PlacementsIO(environment=environment, token=token)

    async def set_custom_field_as_oli_name(resource_id):
        oli_list = await pio.opportunity_line_items.get(id=resource_id)
        oli = oli_list[0]
        oli_attributes = oli.get("attributes", {})
        oli_custom_fields = oli_attributes.get("custom-fields") or {}
        oli_custom_field_value = oli_custom_fields.get(custom_field_name)
        return {"name": oli_custom_field_value}

    results = await pio.opportunity_line_items.update(
        opportunity_line_items, attributes=set_custom_field_as_oli_name
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
        "--opportunity_line_items",
        type=lambda s: [int(item) for item in s.split(",")],
        help="A comma-separated list of opportunity line item ids",
    )
    parser.add_argument(
        "--custom_field_name",
        type=str,
        help="The name of the custom field to use as the new opportunity line item name",
    )
    args = parser.parse_args()
    asyncio.run(set_opportunity_line_item_name_from_custom_field(**vars(args)))
