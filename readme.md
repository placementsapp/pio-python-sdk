# Placements.io Python Client

Alpha version of Python Client to access and update resources easily within the Placements.io API

## Installation

This package is not yet published to PyPi and must be installed locally.

Run the following command to install:
```
pip install $(pwd)
```

## Secrets and Environment management

### Environment Selection
Environments must be passed as a parameter to the PlacementsIO class:
```python
pio = PlacementsIO(environment="staging")
```

The default environment if not provided is "staging". Possible values:
- production
- edge
- staging

### Secrets

Secrets may either be set in an environment variable or a parameter to the PlacementsIO class:
```python
pio = PlacementsIO(environment="staging", token="...")
```

Environment variable names prioritize specific environments over the generic `PLACEMENTS_IO_API_TOKEN`.

Possible environment variables:
- PLACEMENTS_IO_API_TOKEN_PRODUCTION
- PLACEMENTS_IO_API_TOKEN_EDGE
- PLACEMENTS_IO_API_TOKEN_STAGING
- PLACEMENTS_IO_API_TOKEN


## Using examples

Predefined examples are available within the [example](/example/) folder. These examples can be used from the command line

A sample command is provided at the top of each example which uses credential management from 1Password.

### 1Password
If you are using [1Password's CLI](https://developer.1password.com/docs/cli/get-started/#step-1-install-1password-cli) you can set environment variables as you run these examples

e.g:

```bash
python example/account/get_recently_modified_accounts.py \
    --environment staging \
    --token $(op read "op://PIO API Keys/PIO - Staging/credential") \
    --modified-since "2024-10-01 00:00:00"
```