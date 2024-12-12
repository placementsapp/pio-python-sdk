"""
python example/product_rate/modify_product_rates_on_rate_cards.py \
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


async def modify_product_rates_on_rate_cards(
    environment: str, token: str, rate_settings: list[dict]
):
    pio = PlacementsIO(environment=environment, token=token)

    updates_by_rate_card = {}
    for setting in rate_settings:
        rate_card_id = setting["rate_card_id"]
        if not updates_by_rate_card.get(rate_card_id):
            updates_by_rate_card[rate_card_id] = []
        updates_by_rate_card[rate_card_id].append(setting)

    updates_by_product_rate = {}
    for rate_card_id, settings in updates_by_rate_card.items():
        rate_card = await pio.rate_cards.get(id=rate_card_id)
        rate_card_relation = rate_card[0]["relationships"]["product-rates"]["links"][
            "related"
        ]
        product_rates = await pio.relationship(rate_card_relation).get()
        has_updated = False
        for product_rate in product_rates:
            product_rate_id = product_rate["id"]
            product_rate_product_id = int(
                product_rate["relationships"]["product"]["data"]["id"]
            )
            update_settings = [
                _ for _ in settings if _["product_id"] == product_rate_product_id
            ]
            if len(update_settings) != 1:
                continue
            update_settings = update_settings[0]

            if not updates_by_product_rate.get(product_rate_id):
                updates_by_product_rate[product_rate_id] = {}
            updates_by_product_rate[product_rate_id] = {
                "attributes": {
                    "cost-per-unit": update_settings["cost_per_unit"],
                },
                "relationships": {
                    "product": {
                        "data": {
                            "type": "products",
                            "id": update_settings["product_id"],
                        }
                    },
                    "rate-card": {
                        "data": {
                            "type": "rate-cards",
                            "id": update_settings["rate_card_id"],
                        },
                    },
                },
            }
            has_updated = True
        if not has_updated:
            print(
                f"Rate card {rate_card_id} does not have matching product rates to update. Skipping.",
                settings,
            )

    async def update_product_rate_attributes(rate_id):
        return updates_by_product_rate[rate_id]["attributes"]

    async def update_product_rate_relationships(rate_id):
        return updates_by_product_rate[rate_id]["relationships"]

    results = await pio.product_rates.update(
        updates_by_product_rate.keys(),
        attributes=update_product_rate_attributes,
        relationships=update_product_rate_relationships,
    )
    print(json.dumps(results, indent=4, default=str))


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
    asyncio.run(modify_product_rates_on_rate_cards(**vars(args)))
