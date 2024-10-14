import os
from pio.client import *

__version__ = "0.0.1"
__all__ = [
    "PlacementsIO",
    "__version__",
    "Accounts",
    "Opportunities",
    "OpportunityLineItems",
    "LineItems",
]
os.environ["PLACEMENTS_IO_CLIENT_VERSION"] = __version__
