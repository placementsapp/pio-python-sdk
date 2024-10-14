"""
python example/account/update_agency_holding_company.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --campaign_ids 1,2,3 \
    --agency_holding_company_account_id 123
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_agency_holding_company(
    environment: str,
    token: str,
    campaign_ids: list[int],
    agency_holding_company_account_id: str,
):
    pio = PlacementsIO(environment=environment, token=token)

    results = await pio.campaigns.update(
        resource_ids=campaign_ids,
        relationships={
            "agency-holding-company": {
                "data": {"type": "accounts", "id": agency_holding_company_account_id}
            }
        },
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the agency holding company for campaigns."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--campaign_ids",
        type=lambda s: [int(item) for item in s.split(",")],
        help="A comma-separated list of campaign ids",
    )
    parser.add_argument(
        "--agency_holding_company_account_id",
        type=int,
        help="The account id of the agency holding company to set for the campaigns.",
    )
    args = parser.parse_args()
    asyncio.run(update_agency_holding_company(**vars(args)))
