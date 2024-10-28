"""
python example/account/get_account_by_id.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --account_id 1548215
"""

import json
import logging
import asyncio

import argparse
from pio.oauth import PlacementsIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_account_id_with_oauth(
    environment: str,
    token: str,
    account_id: int,
):
    """Sample function to get account by ID."""
    pio = PlacementsIO(environment=environment, token=token)
    accounts = await pio.accounts.get(id=account_id)
    # for _ in range(80):
    accounts = await pio.accounts.get(id=account_id)
    print(json.dumps(accounts, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an account by id.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--account_id",
        type=int,
        help="The account ID to get.",
    )
    args = parser.parse_args()
    asyncio.run(get_account_id_with_oauth(**vars(args)))
