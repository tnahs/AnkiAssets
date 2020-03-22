import json
from typing import Dict, Iterator

import aqt

from .defaults import Asset


class AnkiAssetsConfig:

    __config: Dict[str, Dict[str, bool]] = {
        Asset.CSS: {},
        Asset.JS: {},
    }

    """ AnkiAssetsConfig data structure.

        {
            "css": {
                "one.css": True,
                "two.css": True,
                "three.css": True,
            },
            "js": {
                "one.js": True,
                "two.js": True,
                "three.js": True,
            }
        }
    """

    def __init__(self, addon):

        self._addon = addon

        self._load_config()

    @property
    def assets_css(self) -> dict:
        return self.__config[Asset.CSS]

    @property
    def assets_js(self) -> dict:
        return self.__config[Asset.JS]

    def toggle_asset(self, asset_type: str, asset: str) -> None:
        self.__config[asset_type][asset] = not self.__config[asset_type][asset]
        self._save_config()

    def _load_config(self) -> None:

        try:
            with open(self._addon.user_assets_json, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            self._build_config()
        except json.JSONDecodeError:
            aqt.utils.showInfo(
                f"{self._addon.name}: Error loading config... AnkiAssetsConfig "
                f"re-built.\n Please confirm setting by going to Tools > "
                f"{self._addon.preferences_menu_name}"
            )
            self._build_config()
        else:
            self.__config = config
            self._update_config()

    def _update_config(self) -> None:

        self._update_config_by_type(
            asset_type=Asset.CSS, user_assets=self._addon.user_assets_css
        )
        self._update_config_by_type(
            asset_type=Asset.JS, user_assets=self._addon.user_assets_js
        )

        self._save_config()

    def _update_config_by_type(self, asset_type: str, user_assets: Iterator):

        # Need to convert `user_assets` Generator to a List. Otherwise as a
        # Gererator it gets exhausted after the first use.
        user_assets = list(user_assets)  # type: ignore

        new_assets = []
        deleted_assets = []

        # Make a list of all assets currently in the `user_files/[asset_type]`
        # directory that have no entries in `AnkiAssetsConfig.__config`.
        for asset in user_assets:
            if asset in self.__config[asset_type].keys():
                continue
            new_assets.append(asset)

        # Make a list of all assets in `AnkiAssetsConfig.__config` that are not in the
        # `user_files/[asset_type]` directory.
        for asset in self.__config[asset_type].keys():
            if asset in user_assets:
                continue
            deleted_assets.append(asset)

        # Add all the newly added assets to `AnkiAssetsConfig.__config` and set their value
        # to `True`. Meaning the asset is enabled and will be appended to all
        # card templates.
        for new_asset in new_assets:
            self.__config[asset_type][new_asset] = True

        # Remove all the deleted assets from `AnkiAssetsConfig.__config`.
        for deleted_asset in deleted_assets:
            del self.__config[asset_type][deleted_asset]

    def _build_config(self) -> None:

        # Add all assets currently in the `user_files/css` and `user_files/js`
        # directories and set their value to `True`. Meaning the asset is
        # enabled and will be appended to all card templates.

        for asset in self._addon.user_assets_css:
            self.__config[Asset.CSS][asset] = True

        for asset in self._addon.user_assets_js:
            self.__config[Asset.JS][asset] = True

        self._save_config()

    def _save_config(self) -> None:
        with open(self._addon.user_assets_json, "w") as f:
            json.dump(self.__config, f, indent=4)
