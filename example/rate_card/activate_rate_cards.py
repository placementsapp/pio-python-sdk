"""
python example/rate_card/activate_rate_cards.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --rate_cards "992,993,994"
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def activate_rate_cards(environment: str, token: str, rate_cards: list):
    pio = PlacementsIO(environment=environment, token=token)
    status = await pio.rate_cards.update(
        resource_ids=rate_cards, attributes={"active": True}
    )
    print(json.dumps(status, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Activate rate cards.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--rate_cards",
        type=lambda s: [int(i) for i in s.split(",")],
        help="The rate cards to activate (comma-separated).",
    )
    args = parser.parse_args()
    asyncio.run(activate_rate_cards(**vars(args)))