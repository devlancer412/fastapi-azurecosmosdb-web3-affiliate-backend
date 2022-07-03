import os.path
import pathlib

from internal import ConfigBase, UNSET


class Configuration(ConfigBase):
    RPC_URL: str = "https://rinkeby.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
    AFFILIATE_CALL_ID: str = (
        "0xcf856f9756bfa0a667a04a632e2cdbfb2fb9bdd8a09f56c3355f4e6ebdd9ca63"
    )
    PRIVATE_KEY: str = (
        "6f8749b0d24524c8ee094ddac371c8e3ae8771e42505927196b0c8d6b67dd175"
    )

    # Database
    ACCOUNT_HOST: str = "https://affiliate-database.documents.azure.com:443/"
    ACCOUNT_KEY: str = "PdeeJoOY7rTwz7fCoFb91CAZFl9Fy0s2DwN8HbPvRbHAOnzj0p9aJfzFhj691jTc3GdUSGeu6zRfssXFaH3lSQ=="
    COSMOS_DATABASE: str = "AffiliateMarketing"


# --- Do not edit anything below this line, or do it, I'm not your mom ----
defaults = Configuration(autoload=False)
cfg = Configuration()
