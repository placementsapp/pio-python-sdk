"""
python example/user/get_user_by_email.py \
    --email example@example.com
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_user_by_email(environment: str, token: str, email: int):
    pio = PlacementsIO(environment=environment, token=token)
    result = await pio.users.get(email=email)
    print(json.dumps(result, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get information on a rate card.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--email",
        type=str,
        help="The email address of the user to search for.",
    )
    args = parser.parse_args()
    asyncio.run(get_user_by_email(**vars(args)))
