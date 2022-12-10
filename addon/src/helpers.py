import os
import pathlib
from enum import Enum

import aqt


def is_development_mode() -> bool:
    """Returns a bool for whether or not the the add-on is being developed."""

    return "ANKI_ADDON_DEVELOPMENT" in os.environ


class Defaults:
    """A class defining all the add-on's default values."""

    NAME = "AnkiAssets"

    # This name is used for properly setting the path to where the web exports
    # are located. Anki expects this to be: `/_addons/[addon-name]/`. Hard-
    # coding the name can result in missing web assets as depending on how the
    # add-on is installed, its name will be different.
    NAME_INTERNAL = (
        aqt.mw.addonManager.addonFromModule(__name__) if aqt.mw is not None else NAME
    )

    PREFERENCES_NAME = f"{NAME} Preferences"
    PREFERENCES_MENU_NAME = f"{PREFERENCES_NAME}..."
    PREFERENCES_MENU_SHORTCUT = "Ctrl+Shift+G"


class Key:
    """A class defining re-usable strings."""

    ASSETS = "assets"
    ASSETS_JSON = "assets.json"
    USER_FILES = "user_files" if not is_development_mode() else "user_files_dev"


class Paths:
    """A class defining all the add-on's paths.

    The add-on's directory structure is as follows:

    addons21/[addon-name] (1)
    ├── src/
    └── user_files (2)
        ├── assets (3)
        │   ├── css
        │   │   └── ...
        │   └── javascript
        │       └── ...
        └── assets.json (4)
    """

    # (1) The path to the add-on's root directory.
    ADDON_ROOT = pathlib.Path(__file__).parent.parent

    # (2) The path to the add-on's `user_files` directory.
    # --> [path-to-addon]/user_files
    USER_FILES_ROOT = ADDON_ROOT / Key.USER_FILES

    # (3) The path to the add-on's assets root directory.
    # --> [path-to-addon]/user_files/assets
    ASSETS_ROOT = USER_FILES_ROOT / Key.ASSETS

    # (4) The path to the add-on's `asset.json` and `asset.json.bak` files.
    # --> [path-to-addon]/user_files/assets.json
    ASSETS_JSON = USER_FILES_ROOT / Key.ASSETS_JSON
    # --> [path-to-addon]/user_files/assets.json.bak
    ASSETS_JSON_BAK = USER_FILES_ROOT / f"{Key.ASSETS_JSON}.bak"

    # The path to the add-on's web exports root directory.
    # --> /_addons/[addon-name]/user_files/assets
    WEB_ASSETS_ROOT = (
        pathlib.Path("/")
        / "_addons"
        / Defaults.NAME_INTERNAL
        / Key.USER_FILES
        / Key.ASSETS
    )


class Asset(Enum):
    """An Enum representing all possible asset types."""

    CSS = ("css", "CSS", "css")
    JAVASCRIPT = ("javascript", "JavaScript", "js")

    # When an `Enum` is created, the value of the variant, in this case a tuple, is
    # passed into the `__init__` method. Note, however that creating an enum does
    # not require calling it e.g. `Asset()`. Accessing the variant i.e. `Asset.CSS`
    # instantiates it. Accessing one of the attributes is like any other e.g.
    # `Asset.CSS.label`.
    #
    # https://stackoverflow.com/a/70325042/16968574
    def __init__(self, id: str, label: str, extension: str):

        self.id = id
        self.label = label
        self.extension = extension

        # The path to the asset on disk.
        # --> [path-to-addon]/user_files/assets/[label]
        self.asset_root = Paths.ASSETS_ROOT / label

        # The path to the asset in the web exports directory.
        # --> /_addons/[addon-name]/user_files/assets/[label]
        self.web_asset_root = Paths.WEB_ASSETS_ROOT / label
