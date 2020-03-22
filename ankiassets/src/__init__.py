import functools
import json
import pathlib
from typing import Any, Dict, Iterator, Optional

import anki
import aqt


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


class Asset:
    CSS = "css"
    JS = "js"


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

        self._config = AnkiAssetsConfig(addon=self)
        self._preferences = AnkiAssetsPreferences(addon=self, parent=aqt.mw)

    @property
    def config(self) -> "AnkiAssetsConfig":
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


class AnkiAssetsPreferences(aqt.qt.QDialog):

    _minimum_width = 384

    def __init__(self, addon, parent) -> None:
        super().__init__(parent)

        self._addon = addon

        self._init_ui()

    def _init_ui(self) -> None:

        self.setWindowTitle(self._addon.preferences_name)

        #

        layout_css = aqt.qt.QVBoxLayout()
        layout_css.setSpacing(10)
        layout_css.setContentsMargins(5, 5, 5, 5)

        for asset, state in self._addon.user_assets_config_css.items():
            checkbox = self._create_checkbox_item(
                asset_type=Asset.CSS, asset=asset, state=state
            )
            layout_css.addWidget(checkbox)

        #

        layout_js = aqt.qt.QVBoxLayout()
        layout_js.setSpacing(10)
        layout_js.setContentsMargins(5, 5, 5, 5)

        for asset, state in self._addon.user_assets_config_js.items():
            checkbox = self._create_checkbox_item(
                asset_type=Asset.JS, asset=asset, state=state
            )
            layout_js.addWidget(checkbox)

        #

        group_css = aqt.qt.QGroupBox("Stylesheets:")
        group_css.setLayout(layout_css)

        group_js = aqt.qt.QGroupBox("Javascript:")
        group_js.setLayout(layout_js)

        #

        label_loaded_assets = aqt.qt.QLabel("Loaded Assets:")

        #

        layout = aqt.qt.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(label_loaded_assets)
        layout.addSpacing(10)
        layout.addWidget(group_css)
        layout.addSpacing(10)
        layout.addWidget(group_js)

        self.setLayout(layout)

    def _create_checkbox_item(
        self, asset_type: str, asset: str, state: bool
    ) -> aqt.qt.QCheckBox:

        checkbox = aqt.qt.QCheckBox(asset)
        checkbox.setChecked(state)

        checkbox.toggled.connect(
            functools.partial(
                self._addon.config.toggle_asset, asset_type=asset_type, asset=asset,
            )
        )

        return checkbox

    def _set_window_size(self):

        height = self.sizeHint().height()
        width = (
            self._minimum_width
            if self.sizeHint().width() < self._minimum_width
            else self.sizeHint().width()
        )

        self.setFixedSize(width, height)

    def show(self):
        self._set_window_size()
        super().show()


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
