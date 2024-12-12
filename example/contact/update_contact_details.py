"""
python example/contact/update_contact_details.py \
    --attributes '{
    "1502638": {"comments": "Updated contact details"}
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


async def update_contact_details(environment: str, token: str, attributes: dict):
    pio = PlacementsIO(environment=environment, token=token)

    async def update_contact_settings(contact_id):
        return attributes[contact_id]

    results = await pio.contacts.update(
        attributes.keys(),
        attributes=update_contact_settings,
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the start and end date of line items."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of contact IDs with dictionaries of attributes to update.",
    )
    args = parser.parse_args()
    asyncio.run(update_contact_details(**vars(args)))
