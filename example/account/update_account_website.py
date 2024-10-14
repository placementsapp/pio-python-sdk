"""
python example/account/update_account_websites.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --websites '{
    111111: "https://placements.io/",
    222222: "https://app.placements.io/",
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


async def update_account_websites(environment: str, token: str, websites: dict):
    pio = PlacementsIO(environment=environment, token=token)

    async def set_website(account_id):
        return {"website": websites.get(account_id)}

    updated_accounts = await pio.accounts.update_websites(
        websites.keys(), attributes=set_website
    )
    print(json.dumps(updated_accounts, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update the websites of accounts.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--websites",
        type=json.loads,
        help="A dictionary of account ids to websites.",
    )
    args = parser.parse_args()
    asyncio.run(update_account_websites(**vars(args)))
