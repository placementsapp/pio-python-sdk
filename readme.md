# Placements.io Python Client

Alpha version of Python Client to access and update resources easily within the Placements.io API

## Installation

This package is not yet published to PyPi and must be installed locally.

Run the following command to install:

```bash
pip install $(pwd)
```

## Secrets and Environment management

### Environment Selection

Environments must be passed as a parameter to the PlacementsIO class:

```python3
pio = PlacementsIO(environment="staging")
```

The default environment if not provided is "staging". Possible values:

- production
- staging

### API Tokens

API Tokens may either be set in an environment variable or a parameter to the PlacementsIO class:

```python3
pio = PlacementsIO(environment="staging", token="...")
```

Environment variable names prioritize specific environments over the generic `PLACEMENTS_IO_API_TOKEN`.

Possible environment variables:

- PLACEMENTS_IO_API_TOKEN_PRODUCTION
- PLACEMENTS_IO_API_TOKEN_STAGING
- PLACEMENTS_IO_API_TOKEN

API Tokens may be generated in the Placements.io UI:

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

## Using examples

Predefined examples are available within the [example](/example/) folder. These examples can be used from the command line

A sample command is provided at the top of each example which uses credential management from 1Password. 1Password is not required to use these examples and you may replace its usage with plain-text API Tokens.

> Remember: Never share or disclose your API Token. It can be used by anyone to run API calls on your behalf without logging into the Placements.io Platform.

### 1Password

If you are using [1Password's CLI](https://developer.1password.com/docs/cli/get-started/#step-1-install-1password-cli) you can set environment variables as you run these examples

e.g:

```bash
python example/account/get_recently_modified_accounts.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --modified-since "2024-10-01 00:00:00"
```

## Developers

[Poetry](https://pypi.org/project/poetry/) is the build system used to compile the `placements-io-api` PyPi package.

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
