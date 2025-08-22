"""
python example/group/get_group_by_id.py \
    --group_id 1111
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_group_by_id(environment: str, token: str, group_id: int):
    pio = PlacementsIO(environment=environment, token=token)
    group = await pio.groups.get(id=group_id)
    print(json.dumps(group, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get group by id.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--group_id",
        type=int,
        help="The group id to get",
    )
    args = parser.parse_args()
    asyncio.run(get_group_by_id(**vars(args)))
