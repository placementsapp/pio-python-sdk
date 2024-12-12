"""
python example/creative/get_creative.py \
    --creative_id 15700
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_creative(environment: str, token: str, creative_id: int):
    pio = PlacementsIO(environment=environment, token=token)
    creative = await pio.creatives.get(id=creative_id)
    print(json.dumps(creative, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get creative information.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--creative_id",
        type=int,
        help="The creative id to get.",
    )
    args = parser.parse_args()
    asyncio.run(get_creative(**vars(args)))
