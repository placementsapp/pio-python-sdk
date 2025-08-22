"""
python example/opportunity/update_opportunity_attributes.py \
    --push_to_crm True \
    --attributes '{
    "452331": {"start-date": "2024-10-07 00:00:00 -04:00", "end-date": "2024-12-31 11:59:59 -04:00"}
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


async def update_opportunity_attributes(
    environment: str,
    token: str,
    attributes: dict,
    push_to_crm: bool = True,
):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_opportunity_settings(opportunity_id):
        return attributes[opportunity_id]

    results = await pio.opportunities.update(
        attributes.keys(),
        attributes=update_opportunity_settings,
        params={
            "skip_push_to_crm": (not push_to_crm),
        },
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the attributes of opportunities."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--push_to_crm",
        type=lambda v: v.lower() != "false",
        default=True,
        help="Whether to push the changes to the CRM after update.",
    )
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of opportunity IDs to dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_opportunity_attributes(**vars(args)))
