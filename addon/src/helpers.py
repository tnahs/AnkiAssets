import os
import pathlib
from enum import Enum

import aqt


def is_development_mode():
    return "ANKI_ADDON_DEVELOPMENT" in os.environ


class Defaults:
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
    PREFERENCES_MINIMUM_WIDTH = 384


class Key:
    ASSETS = "assets"
    ASSETS_JSON = "assets.json"
    USER_FILES = "user_files" if not is_development_mode() else "user_files_dev"


class Asset(str, Enum):
    CSS = "css"
    JAVASCRIPT = "javascript"


class Extension(str, Enum):
    CSS = "css"
    JAVASCRIPT = "js"


class Paths:

    # addons21/[addon-name]
    # ├── src/
    # └── user_files
    #     ├── assets.json
    #     └── assets
    #         ├── css
    #         │   └── ...
    #         └── javascript
    #             └── ...
    #
    # [path-to-addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [path-to-addon]/user_files
    USER_FILES_ROOT = ADDON_ROOT / Key.USER_FILES
    # [path-to-addon]/user_files/assets.json
    ASSETS_JSON = USER_FILES_ROOT / Key.ASSETS_JSON
    # [path-to-addon]/user_files/assets.json
    ASSETS_JSON_BAK = USER_FILES_ROOT / f"{Key.ASSETS_JSON}.bak"
    # [path-to-addon]/user_files/assets
    ASSETS_ROOT = USER_FILES_ROOT / Key.ASSETS
    # [path-to-addon]/user_files/assets/css
    ASSETS_CSS_ROOT = ASSETS_ROOT / Asset.CSS.value
    # [path-to-addon]/user_files/assets/javascript
    ASSETS_JAVASCRIPT_ROOT = ASSETS_ROOT / Asset.JAVASCRIPT.value

    # /_addons
    WEB_ROOT = pathlib.Path("/_addons")
    # /_addons/[addon-name]/user_files/assets
    WEB_ASSETS_ROOT = WEB_ROOT / Defaults.NAME_INTERNAL / Key.USER_FILES / Key.ASSETS
    # /_addons/[addon-name]/user_files/assets/css
    WEB_ASSETS_CSS_ROOT = WEB_ASSETS_ROOT / Asset.CSS.value
    # /_addons/[addon-name]/user_files/assets/javascript
    WEB_ASSETS_JAVASCRIPT_ROOT = WEB_ASSETS_ROOT / Asset.JAVASCRIPT.value
