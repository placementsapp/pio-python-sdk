import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pio.utility.json_encoder import JSONEncoder


def test_datetime_handling():

    static_datetime = datetime(2024, 12, 1, 13, 00, 00)
    localized_datetime = static_datetime.replace(tzinfo=ZoneInfo("America/New_York"))

    obj = {"date": localized_datetime}
    json_obj = json.dumps(obj, cls=JSONEncoder)

    assert json_obj == '{"date": "2024-12-01T13:00:00-05:00"}'


def test_standard_json():

    input = {"test": True}
    assert json.dumps(input, cls=JSONEncoder) == json.dumps(input)
