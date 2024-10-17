"""
python example/product_rate/add_product_rates_to_rate_cards.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --rate_settings '[
    {
        "rate_card_id": 992,
        "product_id": 183950,
        "cost_per_unit": 10.5
    },
    {
        "rate_card_id": 992,
        "product_id": 183951,
        "cost_per_unit": 11.5
    }
]'
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def add_product_rates_to_rate_cards(
    environment: str, token: str, rate_settings: list[dict]
):
    pio = PlacementsIO(environment=environment, token=token)

    payloads = []
    for setting in rate_settings:
        payloads.append(
            {
                "attributes": {
                    "cost-per-unit": setting["cost_per_unit"],
                },
                "relationships": {
                    "product": {
                        "data": {"type": "products", "id": setting["product_id"]}
                    },
                    "rate-card": {
                        "data": {"type": "rate-cards", "id": setting["rate_card_id"]}
                    },
                },
            }
        )
    new_product_rates = await pio.product_rates.create(payloads)
    print(json.dumps(new_product_rates, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add product rates to rate cards.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--rate_settings",
        type=json.loads,
        help="The rate settings to add. Must be a list of dictionaries with keys: product_id, rate_card_id, cost_per_unit",
    )
    args = parser.parse_args()
    asyncio.run(add_product_rates_to_rate_cards(**vars(args)))
