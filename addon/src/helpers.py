import os
import pathlib
from enum import Enum

import aqt


class Key:
    USER_FILES = (
        "user_files"
        if not os.environ.get("ANKI_ADDON_DEV", False)
        else "user_files_dev"
    )
    ASSETS_JSON = "assets.json"
    ASSETS = "assets"


class E_Asset(str, Enum):
    CSS = "css"
    JS = "js"


class Defaults:
    NAME = "AnkiAssets"
    NAME_INTERNAL = aqt.mw.addonManager.addonFromModule(__name__)

    PREFERENCES_NAME = f"{NAME} Preferences"
    PREFERENCES_MENU_NAME = f"{PREFERENCES_NAME}..."
    PREFERENCES_MENU_SHORTCUT = "Ctrl+Shift+G"
    PREFERENCES_MINIMUM_WIDTH = 384

    # [/absolute/path/to/addon]
    ADDON_ROOT = pathlib.Path(__file__).parent.parent
    # [/absolute/path/to/addon]/user_files
    USER_FILES = ADDON_ROOT / Key.USER_FILES
    # [/absolute/path/to/addon]/user_files/assets.json
    ASSETS_JSON = USER_FILES / Key.ASSETS_JSON
    # [/absolute/path/to/addon]/user_files/assets
    ASSETS_PATH = USER_FILES / Key.ASSETS
    # [/absolute/path/to/addon]/user_files/assets/css
    ASSETS_CSS_PATH = ASSETS_PATH / E_Asset.CSS.value
    # [/absolute/path/to/addon]/user_files/assets/js
    ASSETS_JS_PATH = ASSETS_PATH / E_Asset.JS.value

    # /_addons
    WEB_ROOT = pathlib.Path("/_addons")
    # /_addons/[addon-name]/user_files/assets
    WEB_ASSETS_PATH = WEB_ROOT / NAME_INTERNAL / Key.USER_FILES / Key.ASSETS
    # /_addons/[addon-name]/user_files/assets/css
    WEB_ASSETS_CSS_PATH = WEB_ASSETS_PATH / E_Asset.CSS.value
    # /_addons/[addon-name]/user_files/assets/js
    WEB_ASSETS_JS_PATH = WEB_ASSETS_PATH / E_Asset.JS.value
