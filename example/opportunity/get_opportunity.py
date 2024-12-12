"""
python example/opportunity/get_opportunity.py \
    --opportunity_id 419972
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_opportunity(environment: str, token: str, opportunity_id: int):
    pio = PlacementsIO(environment=environment, token=token)
    opportunity = await pio.opportunities.get(id=opportunity_id)
    print(json.dumps(opportunity, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get opportunity by id.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--opportunity_id",
        type=int,
        help="The opportunity id.",
    )
    args = parser.parse_args()
    asyncio.run(get_opportunity(**vars(args)))
