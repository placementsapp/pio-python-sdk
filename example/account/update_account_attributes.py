"""
python example/account/update_account_attributes.py \
    --push_to_ad_server True \
    --push_to_crm True \
    --attributes '{
    "2": {"website": "http://example.com"}
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


async def update_account_attributes(
    environment: str,
    token: str,
    attributes: dict,
    push_to_ad_server: bool = True,
    push_to_crm: bool = True,
):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_account_settings(account_id):
        return attributes[account_id]

    results = await pio.accounts.update(
        attributes.keys(),
        attributes=update_account_settings,
        params={
            "skip_push_to_ad_server": (not push_to_ad_server),
            "skip_push_to_crm": (not push_to_crm),
        },
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update the attributes of accounts.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--push_to_ad_server",
        type=lambda v: v.lower() != "false",
        default=True,
        help="Whether to push the changes to the ad server after update.",
    )
    parser.add_argument(
        "--push_to_crm",
        type=lambda v: v.lower() != "false",
        default=True,
        help="Whether to push the changes to the CRM after update.",
    )
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of account IDs to dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_account_attributes(**vars(args)))
