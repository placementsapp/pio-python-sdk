import json
from pio import PlacementsIO
import logging
import asyncio
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
# logging.getLogger("pio").setLevel(logging.DEBUG)


async def get_opportunities():
    pio = PlacementsIO(environment="staging")
    modified_since = datetime.datetime(2024, 9, 4, 0, 0, 0)
    opportunities = await pio.opportunities(modified_since=modified_since)
    print(json.dumps(opportunities, indent=4, default=str))
    print(len(opportunities))
    print([opportunity.get("id") for opportunity in opportunities])


if __name__ == "__main__":
    asyncio.run(get_opportunities())
    # asyncio.run(get_recently_modified_accounts())
