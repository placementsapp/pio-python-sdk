"""
python example/report/create_line_item_report.py \
    --lookback_days 7
"""

import json
from pio import PlacementsIO
import logging
import asyncio
import argparse
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("pio").setLevel(logging.DEBUG)


async def create_line_item_report(environment: str, token: str, lookback_days: int):

    pio = PlacementsIO(environment=environment, token=token)
    today = datetime.datetime.now(datetime.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_date = today - datetime.timedelta(days=lookback_days)
    report = await pio.reports.create(start_date=start_date)
    result = await pio.reports.data(report)
    print(json.dumps(result, indent=4, default=str))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a line item report.")
    parser.add_argument(
        "--environment",
        type=str,
        help="The environment to use. Either `production` or `staging`.",
    )
    parser.add_argument("--token", type=str, help="The token to use.")
    parser.add_argument(
        "--lookback_days",
        type=int,
        help="The number of days to lookback from today when generating the report.",
    )
    args = parser.parse_args()
    asyncio.run(create_line_item_report(**vars(args)))
