import pathlib
from typing import Any, Iterator, Optional

import aqt

from . import config, preferences
from .defaults import Asset


# TODO: Documentation!
# TODO: Clean up inter-class API.
# TODO: Clearer variable names
#           `user_assets_config_css`
#           `user_assets_config_js`
#           `user_assets_css`
#           `user_assets_js`
#           etc.
# TODO: Add `reload assets` button in Preferences.
# TODO: Add message in `clayout` that there are loaded assets.


class AnkiAssets:

    name = "AnkiAssets"
    preferences_name = f"{name} Preferences"
    preferences_menu_name = f"{preferences_name}..."
    preferences_menu_shortcut = "ctrl+shift+g"

    # [/absolute/path/to/addons]/ankiassets
    root = pathlib.Path(__file__).parent.parent

    user_root = root / "user_files"
    user_assets_path = user_root / "assets"
    user_assets_css_path = user_root / "assets" / Asset.CSS
    user_assets_js_path = user_root / "assets" / Asset.JS
    user_assets_json = user_root / "assets.json"

    # Add-ons may expose their own web assets by utilizing
    # aqt.addons.AddonManager.setWebExports(). Web exports registered
    # in this manner may then be accessed under the `/_addons` subpath.
    #
    # via https://github.com/ankitects/anki/blob/3d7f643184cf9625293a397e1a73109659b77734/qt/aqt/webview.py#L132
    web_exports_root = pathlib.Path("/_addons") / root.name / "user_files" / "assets"

    # /_addons/ankiassets/user_files/assets/css
    web_exports_assets_css_path = web_exports_root / Asset.CSS

    # /_addons/ankiassets/user_files/assets/js
    web_exports_assets_js_path = web_exports_root / Asset.JS

    def __init__(self) -> None:

        self._config = config.AnkiAssetsConfig(addon=self)
        self._preferences = preferences.AnkiAssetsPreferences(addon=self, parent=aqt.mw)

    @property
    def config(self) -> config.AnkiAssetsConfig:
        return self._config

    @property
    def user_assets_config_css(self) -> dict:
        return self._config.assets_css

    @property
    def user_assets_config_js(self) -> dict:
        return self._config.assets_js

    @property
    def user_assets_css(self) -> Iterator[str]:
        return self._user_assets_by_type(
            asset_type=Asset.CSS, assets_path=self.user_assets_css_path
        )

    @property
    def user_assets_js(self) -> Iterator[str]:
        return self._user_assets_by_type(
            asset_type=Asset.JS, assets_path=self.user_assets_js_path
        )

    def _user_assets_by_type(
        self, asset_type: str, assets_path: pathlib.Path
    ) -> Iterator[str]:

        # "ext" --> "*.ext"
        asset_glob = f"*.{asset_type}"

        for path in assets_path.glob(asset_glob):

            filename = path.name

            # Ignore directories.
            if path.is_dir():
                continue

            # Ignore hidden files.
            if filename.startswith("."):
                continue

            # Ignore private files.
            if filename.startswith("_"):
                continue

            # [/absolute/path/to/addons]/ankiassets/user_files/assets/css/[asset-name].css --> [asset-name].css
            # [/absolute/path/to/addons]/ankiassets/user_files/assets/js/[asset-name].js --> [asset-name].js
            yield str(path.relative_to(assets_path))

    def _append_preferences_menu(self) -> None:

        action = aqt.qt.QAction(aqt.mw)
        action.setText(self.preferences_menu_name)
        action.setShortcut(self.preferences_menu_shortcut)

        action.triggered.connect(self._preferences.show)

        aqt.mw.form.menuTools.addAction(action)

    def setup(self) -> None:
        """ This function defines and connects AnkiAssets to Anki. Hooks
        are prefixed with `hook__`. """

        self._append_preferences_menu()

        def hook__append_assets(
            web_content: aqt.webview.WebContent, context: Optional[Any]
        ) -> None:

            if isinstance(context, aqt.editor.Editor):
                return

            # Add-ons may expose their own web assets by utilizing
            # aqt.addons.AddonManager.setWebExports(). Web exports registered
            # in this manner may then be accessed under the `/_addons` subpath.
            #
            # E.g., to allow access to a `my-addon.js` and `my-addon.css`
            # residing in a "web" subfolder in your add-on package, first
            # register the corresponding web export:
            #
            #   > from aqt import mw
            #   > mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")
            #
            # via https://github.com/ankitects/anki/blob/3d7f643184cf9625293a397e1a73109659b77734/qt/aqt/webview.py#L132
            aqt.mw.addonManager.setWebExports(__name__, r".*")

            for css_asset, enabled in self.user_assets_config_css.items():

                if not enabled:
                    continue

                # /_addons/ankiassets/user_files/assets/css/[asset-name].css
                path = str(self.web_exports_assets_css_path / css_asset)
                web_content.css.append(path)

            for js_asset, enabled in self.user_assets_config_js.items():

                if not enabled:
                    continue

                # /_addons/ankiassets/user_files/assets/js/[asset-name].js
                path = str(self.web_exports_assets_js_path / js_asset)
                web_content.js.append(path)

        aqt.gui_hooks.webview_will_set_content.append(hook__append_assets)
