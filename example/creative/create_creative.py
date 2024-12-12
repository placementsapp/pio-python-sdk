"""
python example/creative/create_creative.py \
    --account_id 1549397 \
    --attributes '{
        "name": "Sample Creative",
        "ad-server": "offline",
        "creative-type": "video",
        "status": "ACTIVE",
        "width": 640,
        "height": 480,
        "click-target": "https://archive.org/details/SnackBarCartoonLeprechaun",
        "media-url": "https://archive.org/download/SnackBarCartoonLeprechaun/snackbar_leprechan_cartoon.mp4"
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


async def create_creative(
    environment: str, token: str, account_id: int, attributes: dict
):
    pio = PlacementsIO(environment=environment, token=token)

    creative_payload = [
        {
            "type": "creatives",
            "attributes": attributes,
            "relationships": {
                "account": {"data": {"type": "accounts", "id": account_id}}
            },
        }
    ]

    creative = await pio.creatives.create(creative_payload)
    print(json.dumps(creative, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add creative for an account.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--account_id",
        type=int,
        help="The account id to associate the creative with.",
    )
    parser.add_argument(
        "--attributes",
        type=json.loads,
        help="A dictionary of attributes for the creative.",
    )
    args = parser.parse_args()
    asyncio.run(create_creative(**vars(args)))
