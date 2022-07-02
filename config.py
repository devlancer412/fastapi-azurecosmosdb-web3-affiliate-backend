import os.path
import pathlib

from internal import ConfigBase, UNSET


class Configuration(ConfigBase):
    RPC_URL: str = UNSET
    AFFILIATE_CALL_ID: str = UNSET
    PRIVATE_KEY: str = UNSET

    # Database
    ACCOUNT_HOST: str = UNSET
    ACCOUNT_KEY: str = UNSET
    COSMOS_DATABASE: str = UNSET


# --- Do not edit anything below this line, or do it, I'm not your mom ----
defaults = Configuration(autoload=False)
cfg = Configuration()
