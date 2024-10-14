"""
python example/rate_card/get_rate_card.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --rate_card 992
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_rate_card(environment: str, token: str, rate_card: int):
    pio = PlacementsIO(environment=environment, token=token)
    result = await pio.rate_cards.get(id=rate_card)
    print(json.dumps(result, indent=4, default=str))
    for rate_card_object in result:
        product_rates = (
            rate_card_object.get("relationships", {})
            .get("product-rates", {})
            .get("links", {})
            .get("related")
        )
        if product_rates:
            product_rates = await pio.relationship(product_rates).get()
            print(json.dumps(product_rates, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get information on a rate card.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. One of: production, edge, or staging",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--rate_card",
        type=int,
        help="The rate card id",
    )
    args = parser.parse_args()
    asyncio.run(get_rate_card(**vars(args)))
