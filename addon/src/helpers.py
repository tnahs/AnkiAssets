import os
import pathlib
from enum import Enum

import aqt


class E_Asset(str, Enum):
    CSS = "css"
    JS = "js"


class Key:
    ASSETS = "assets"
    ASSETS_JSON = "assets.json"
    USER_FILES = (
        "user_files"
        if "ANKI_ADDON_DEVELOPMENT" not in os.environ
        else "user_files__dev"
    )


class Defaults:
    NAME = "AnkiAssets"
    NAME_INTERNAL = (
        aqt.mw.addonManager.addonFromModule(__name__) if aqt.mw is not None else NAME
    )

    # [/absolute/path/to/addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [/absolute/path/to/addon]/user_files
    USER_FILES = ADDON_ROOT / Key.USER_FILES
    # [/absolute/path/to/addon]/user_files/assets.json
    ASSETS_JSON = USER_FILES / Key.ASSETS_JSON
    # [/absolute/path/to/addon]/user_files/assets
    ASSETS = USER_FILES / Key.ASSETS
    # [/absolute/path/to/addon]/user_files/assets/css
    ASSETS_CSS = ASSETS / E_Asset.CSS.value
    # [/absolute/path/to/addon]/user_files/assets/js
    ASSETS_JS = ASSETS / E_Asset.JS.value

    # /_addons
    WEB_ROOT = pathlib.Path("/_addons")
    # /_addons/[addon-name]/user_files/assets
    WEB_ASSETS = WEB_ROOT / NAME_INTERNAL / Key.USER_FILES / Key.ASSETS
    # /_addons/[addon-name]/user_files/assets/css
    WEB_ASSETS_CSS = WEB_ASSETS / E_Asset.CSS.value
    # /_addons/[addon-name]/user_files/assets/js
    WEB_ASSETS_JS = WEB_ASSETS / E_Asset.JS.value

    PREFERENCES_NAME = f"{NAME} Preferences"
    PREFERENCES_MENU_NAME = f"{PREFERENCES_NAME}..."
    PREFERENCES_MENU_SHORTCUT = "Ctrl+Shift+G"
    PREFERENCES_MINIMUM_WIDTH = 384
