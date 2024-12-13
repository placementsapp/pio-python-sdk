# Placements.io Python Software Development Kit

Placements.io is the world’s leading operating system for digital advertising. By making advertising more intelligent, efficient and transparent — for buyers and sellers — we’re making the industry more profitable for everyone.

This Python Software Development Kit (SDK) provides programmers with the resources to more effectively interface with the Placements.io API. The SDK also handles events such as 429 HTTP responses, batching of large requests, and execution of asynchronous HTTP requests which provides faster results and reduced development time.

## Installation

```
pip install placements-io
```

## Secrets and environment management

An environment name and token are required when instantiating the `PlacementsIO` class.

These may be set in plain-text in code, through environment variables, or a combination of the both:

```python3
pio = PlacementsIO(environment="staging", token="...")
```

```bash
export PLACEMENTS_IO_ENVIRONMENT="staging"
export PLACEMENTS_IO_TOKEN="..."
```

Alternatively the following environment specific variables may be used which take presence over the environment agnostic `PLACEMENTS_IO_TOKEN` environment variable:

- `PLACEMENTS_IO_TOKEN_PRODUCTION`
- `PLACEMENTS_IO_TOKEN_STAGING`

Possible values for environment are:

- production
- staging

API tokens may be generated in the Placements.io UI:

- [Production API Tokens](https://app.placements.io/settings/tokens)
- [Staging API Tokens](https://staging.placements.io/settings/tokens)

### OAuth2

OAuth2 authentication may be alternatively be used in place of API Tokens by using the `PlacementsIO_OAuth` class along with the application ID and client secret:

```python3
pio = PlacementsIO_OAuth(
    environment="staging",
    application_id="...",
    client_secret="...",
)
```

OAuth application ID and secrets may be obtained by contacting support@placements.io. You will need to provide a name for you application and a redirect URL (http://localhost:17927 is the default used in the `PlacementsIO_Oauth` class)

You may also provide a customized redirect URL and scopes to your OAuth application:

```python3
pio = PlacementsIO_OAuth(
    environment="staging",
    application_id="...",
    client_secret="...",
    redirect_host="https://example.com",
    redirect_port=443,
    scopes=["account_read"],
)
```

## Using command line examples

Predefined examples are available within the [example](https://github.com/placementsapp/pio-python-sdk/tree/main/example) folder. These examples can be used from the command line.

A sample command is provided at the top of each example which utilizes operating system variables to provide the environment name and token. e.g:

```bash
export PLACEMENTS_IO_ENVIRONMENT="staging"
export PLACEMENTS_IO_TOKEN_STAGING="..."
```

```bash
python example/account/get_recently_modified_accounts.py \
    --modified-since "2024-10-01 00:00:00 +00:00"
```

Alternatively if you are using the [1Password's CLI](https://developer.1password.com/docs/cli/get-started/#step-1-install-1password-cli) you can set environment variables as you run these examples by also providing the environment and token variables. e.g:

```bash
python example/account/get_recently_modified_accounts.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --modified-since "2024-10-01 00:00:00 +00:00"
```

## SDK Methods

### Service resources

Each API resource available in the Placements.io Public API is given an attribute on the PlacementsIO class which allows you to interact specifically with that resource service. These resources are asynchronous methods that must be awaited:

```
import asyncio
from pio import PlacementsIO

async def main():
    pio = PlacementsIO(environment="...", token="...")
    await pio.accounts.get(...)
    await pio.accounts.create(...)
    await pio.accounts.update(...)

asyncio.run(main())
```

The following service resources are available:

- accounts
- campaigns
- contacts
- creatives
- custom_fields
- external_users
- groups
- line_items
- line_item_creative_associations
- opportunities
- opportunity_line_items
- packages
- products
- product_rates
- rate_cards
- reports
- users

### Resource Methods

Each resource provides the following methods:

- get
- create
- update

Except for the report resource which provides the following methods:

- get
- create
- data

### Get

Requests to the `get` method will provide a HTTP get request to the Placements.io resource.

```python3
import asyncio
from pio import PlacementsIO

async def main():
    pio = PlacementsIO(environment="...", token="...")
    accounts = await pio.accounts.get()

asyncio.run(main())
```

Providing no parameters will return all of the data for that resource; however it is recommended to use parameters to define the data you need to access:

| Parameter     | Summary                                                                     | Example                                                    |
| ------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------- |
| (filter name) | Resource filters [defined in API](https://api.placements.io/doc/#resources) | `pio.line_items.get(id=1234)`                              |
| include       | Includes additional data from resource relationships                        | `pio.line_items.get(include=[bill-to-account,advertiser])` |
| fields        | Return specified attributes (aka Sparse Fieldsets)                          | `pio.line_items.get(fields=['start-date'])`                |
| params        | Additional URL parameters                                                   | `pio.line_items.get(params={"stats: True})`                |

The response from the SDK will be a list of dictionaries, regardless of the number of results that will be returned.

### Update

Requests to the `update` method will provide a HTTP patch requests to the Placements.io resource for the resource ids that are specified.

```python3
import asyncio
from pio import PlacementsIO

async def main():
    pio = PlacementsIO(environment="...", token="...")
    accounts = await pio.accounts.update(
        resource_ids: [1111, 2222]
        attributes: {"website": "http://example.com"}
    )

asyncio.run(main())
```

The following parameters may be passed to the update method:
| Parameter | Summary | Example|
| --------- | ------- | ------ |
| resource_ids | Required. A list of the ids to modify | `pio.accounts.update(resource_ids=[1111, 2222], ...)` |
| attributes | Required if `relationships` parameter is not provided. The attribute values of the resource. | `pio.line_items.update(attributes={"active": True}, ...)` |
| relationships | Required if `attributes` parameter is not provided. The relationships to other resources. | `pio.line_items.update(relationships={"owner": {"data": {"type": "users", "id": "1111"}}}, ...)` |
| params | Additional URL parameters | `pio.line_items.update(params={"skip_push_to_ad_server: True})` |

Both `attributes` and `relationships` values may be a dictionary or an asynchronous function.

Dictionary values will be applied to all of the provided resource ids.

Asynchronous functions will be called with the resource id being processed and should return a dictionary of the desired attributes for that resource id. This allows you to perform pre=processing of data before it is sent to the API. For example the below code shows a simple example where the opportunity line item title is updated to be the value shown in a custom field:

```python3
import asyncio
from pio import PlacementsIO

async def main():
    pio = PlacementsIO(environment=environment, token=token)

    async def set_custom_field_as_oli_name(resource_id):
        oli_list = await pio.opportunity_line_items.get(id=resource_id)
        oli = oli_list[0]
        oli_attributes = oli.get("attributes", {})
        oli_custom_fields = oli_attributes.get("custom-fields") or {}
        oli_custom_field_value = oli_custom_fields.get("custom_field_name")
        return {"name": oli_custom_field_value}

    results = await pio.opportunity_line_items.update(
        resource_ids=[1111, 2222],
        attributes=set_custom_field_as_oli_name
    )

asyncio.run(main())
```

### Create

Create allows you to create new objects within Placements.io. This method expects a list of dictionaries that should be created for a single service.

```python3
import asyncio
from pio import PlacementsIO

async def main():
    pio = PlacementsIO(environment=environment, token=token)

    creative_payload = [
        {
            "type": "creatives",
            "attributes": {...},
            "relationships": {
                "account": {"data": {"type": "accounts", "id": [1111]}}
            },
        },
        {
            "type": "creatives",
            "attributes": {...},
            "relationships": {
                "account": {"data": {"type": "accounts", "id": [2222]}}
            },
        }
    ]

    creatives = await pio.creatives.create(creative_payload)

asyncio.run(main())
```

### Report Methods

The report service has different inputs to the `.get()` and `.create()` methods and also has an additional `.data()` method.

A report must be created before it can be retrieved.:

```python3
import asyncio
from pio import PlacementsIO

async def main():
    pio = PlacementsIO(environment=environment, token=token)

    report = await pio.reports.create()
    result = await pio.reports.data(report)

asyncio.run(main())
```

The create method has the following parameters and default values:
| Parameter | Data type | Default |
| --------- | ------- | ------ |
| start_date | datetime | Todays date at 00:00:00 UTC |
| end_date | datetime | Todays date at 23:59:59 UTC |
| columns | list of strings | Defaults to [all columns](https://github.com/placementsapp/pio-python-sdk/blob/main/pio/model/report.py) |

The `create` service then returns an integer of the report that has been queued. This id can then be passed into either the `get` method to return the response from the report service for that report, or the `data` service which will poll the report service until the service responds with a success or failure message. The data service will respond with the list of report data which can then be used in further analysis such as through the [Pandas](https://pypi.org/project/pandas/) Python package:

```python3
import asyncio
import pandas as pd
from pio import PlacementsIO

async def main():
    pio = PlacementsIO(environment=environment, token=token)

    report = await pio.reports.create()
    result = await pio.reports.data(report)
    dataframe = pd.DataFrame(result)

asyncio.run(main())
```

## Developers

[Poetry](https://pypi.org/project/poetry/) is the build system used to compile the `placements-io` PyPi package.

### Local Installation

Run the following command to install the package locally

```bash
pip install $(pwd)
```

### Testing

Testing is coordinated with [tox](https://pypi.org/project/tox/) and run through Poetry.

To run tests:

```bash
poetry run tox
```
