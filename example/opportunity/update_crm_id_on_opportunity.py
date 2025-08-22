"""
python example/opportunity/update_crm_id_on_opportunity.py \
    --push_to_crm True \
    --opportunity_id 11111 \
    --salesforce_id 'abc-123'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_salesforce_id_on_opportunity(
    environment: str,
    token: str,
    opportunity_id: int,
    salesforce_id: str,
    push_to_crm: bool = True
):
    pio = PlacementsIO(environment=environment, token=token)

    results = await pio.opportunities.update(
        resource_ids=[opportunity_id],
        attributes={"salesforce-id": salesforce_id},
        params={
            "skip_push_to_crm": (not push_to_crm),
        },
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the ad server id for opportunity."
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
        "--opportunity_id",
        type=int,
        help="The opportunity id to update",
    )
    parser.add_argument(
        "--salesforce_id",
        type=str,
        help="The ad server id to set for the opportunity.",
    )
    args = parser.parse_args()
    asyncio.run(update_salesforce_id_on_opportunity(**vars(args)))
