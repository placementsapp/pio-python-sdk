"""
python example/account/archive_account_by_name.py \
    --account_name "Example Inc, Example Corp" \
    --archive True
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def archive_account_by_name(
    environment: str,
    token: str,
    account_name: list,
    archive: bool,
):
    pio = PlacementsIO(environment=environment, token=token)

    accounts_by_name = []
    for name in account_name:
        accounts = await pio.accounts.get(name=name)
        accounts_by_name.extend(accounts)
    account_ids = [account["id"] for account in accounts_by_name if account.get("id")]
    results = await pio.accounts.update(account_ids, attributes={"archived": archive})
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Archive or unarchive accounts by name."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--account_name",
        type=lambda s: s.split(","),
        help="A comma-separated list of account names to update.",
    )
    parser.add_argument(
        "--archive",
        type=bool,
        help="Whether to archive the account. Either `True` or `False`.",
    )
    args = parser.parse_args()
    asyncio.run(archive_account_by_name(**vars(args)))
