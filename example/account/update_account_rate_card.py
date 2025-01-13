"""
python example/account/update_account_rate_card.py \
    --account_id 1549397 \
    --rate_card_id 994
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_account_rate_card(
    environment: str,
    token: str,
    account_id: int,
    rate_card_id: int = None,
):
    pio = PlacementsIO(environment=environment, token=token)

    results = await pio.accounts.update(
        [account_id], relationships={"rate-card": {"data": {"id": rate_card_id}} if rate_card_id else None}
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update account rate card")
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
        "--rate_card_id",
        type=int,
        help="The rate card id to relate to the account",
    )
    args = parser.parse_args()
    asyncio.run(update_account_rate_card(**vars(args)))
