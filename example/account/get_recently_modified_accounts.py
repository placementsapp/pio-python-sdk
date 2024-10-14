"""
python example/account/get_recently_modified_accounts.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --modified-since "2024-10-01 00:00:00"
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import datetime
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_recently_modified_accounts(
    environment: str, token: str, modified_since: datetime.datetime
):
    pio = PlacementsIO(environment=environment, token=token)
    accounts = await pio.accounts.get(modified_since=modified_since)
    print(json.dumps(accounts, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get recently modified accounts.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--modified-since",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S"),
        help="The datetime to filter accounts modified since (format: 'YYYY-MM-DD HH:MM:SS').",
    )
    args = parser.parse_args()
    asyncio.run(get_recently_modified_accounts(**vars(args)))
