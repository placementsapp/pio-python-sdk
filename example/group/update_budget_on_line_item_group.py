"""
python example/account/update_budget_on_line_item_group.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --group_ids 1,2,3 \
    --budget 1234.56
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def update_budget_on_line_item_group(
    environment: str,
    token: str,
    group_ids: list[int],
    budget: float,
):
    pio = PlacementsIO(environment=environment, token=token)

    results = await pio.groups.update(
        resource_ids=group_ids,
        attributes={"budget": budget},
    )
    print(json.dumps(results, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update the budget for line item groups."
    )
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--group_ids",
        type=lambda s: [int(item) for item in s.split(",")],
        help="A comma-separated list of line item group ids",
    )
    parser.add_argument(
        "--budget",
        type=float,
        help="The budget to set for the line item groups.",
    )
    args = parser.parse_args()
    asyncio.run(update_budget_on_line_item_group(**vars(args)))
