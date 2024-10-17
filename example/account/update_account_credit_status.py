"""
python example/account/update_account_credit_status.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --account_ids 1,2,3 \
    --credit_status 'ACTIVE'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_account_credit_status(
    environment: str,
    token: str,
    account_ids: list[int],
    credit_status: str,
):
    pio = PlacementsIO(environment=environment, token=token)

    results = await pio.accounts.update(
        account_ids, attributes={"credit-status": credit_status.upper()}
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update account credit status.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--account_ids",
        type=lambda s: [int(item) for item in s.split(",")],
        help="A comma-separated list of account ids",
    )
    parser.add_argument(
        "--credit_status",
        type=str,
        help="The new credit status to set for the accounts. "
        "One of: ON_HOLD, ACTIVE, CREDIT_STOP, INACTIVE, or BLOCKED",
    )
    args = parser.parse_args()
    asyncio.run(update_account_credit_status(**vars(args)))
