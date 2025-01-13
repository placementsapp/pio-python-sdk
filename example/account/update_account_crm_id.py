"""
python example/account/update_account_crm_id.py \
    --account_id 1111 \
    --crm_id 'CRM-1234'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_account_crm_id(
    environment: str,
    token: str,
    account_id: int,
    crm_id: str = None,
):
    pio = PlacementsIO(environment=environment, token=token)

    results = await pio.accounts.update(
        [account_id], attributes={"salesforce-id": crm_id}
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update account crm id")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--account_id",
        type=int,
        help="The account id to update",
    )
    parser.add_argument(
        "--crm_id",
        type=str,
    )
    args = parser.parse_args()
    asyncio.run(update_account_crm_id(**vars(args)))
