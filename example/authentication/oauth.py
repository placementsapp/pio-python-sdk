"""
python example/authentication/oauth.py \
    --environment staging \
    --application_id $(op read "op://PIO API Keys/OAuth2 - Staging/application_id") \
    --client_secret $(op read "op://PIO API Keys/OAuth2 - Staging/secret") \
    --account_id 1562763
"""

import json
import logging
import asyncio

import argparse
from pio.oauth import PlacementsIO_OAuth

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_account_id_with_oauth(
    environment: str,
    application_id: str,
    client_secret: str,
    account_id: int,
):
    """Sample function to get recently modified accounts using OAuth."""
    pio = PlacementsIO_OAuth(
        environment=environment,
        application_id=application_id,
        client_secret=client_secret,
    )
    accounts = await pio.accounts.get(id=account_id)
    print(json.dumps(accounts, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get an account by id.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument(
        "--application_id", type=str, help="The OAuth2 application ID to use."
    )
    parser.add_argument(
        "--client_secret", type=str, help="The OAuth2 client secret to use."
    )
    parser.add_argument(
        "--account_id",
        type=int,
        help="The account ID to get.",
    )
    args = parser.parse_args()
    asyncio.run(get_account_id_with_oauth(**vars(args)))
