import os
import pathlib
from typing import Any, Iterator, Optional, Tuple

import aqt
import aqt.gui_hooks
from aqt.clayout import CardLayout
from aqt.reviewer import Reviewer
from aqt.webview import WebContent
from PyQt5.QtWidgets import QAction

from .config import Config
from .helpers import Defaults, E_Asset, Key
from .views import PreferencesView


class AnkiAssets:
    def __init__(self) -> None:
        self.__config = Config(addon=self)
        self.__preferences_view = PreferencesView(addon=self, parent=aqt.mw)

    @property
    def config(self) -> Config:
        return self.__config

    def assets(self, type: E_Asset) -> Tuple[str, ...]:

        if type == E_Asset.CSS:
            return tuple(
                self.iter_assets(
                    type=E_Asset.CSS,
                    path=Defaults.ASSETS_CSS_PATH,
                )
            )

        if type == E_Asset.JS:
            return tuple(
                self.iter_assets(
                    type=E_Asset.JS,
                    path=Defaults.ASSETS_JS_PATH,
                )
            )

    @staticmethod
    def iter_assets(type: E_Asset, path: pathlib.Path) -> Iterator[str]:

        # "ext" --> "**/*.ext"
        asset_glob = f"**/*.{type.value}"

        for item in path.glob(asset_glob):

            # Ignore directories.
            if item.is_dir():
                continue

            # Ignore hidden files.
            if item.name.startswith("."):
                continue

            # Ignore private files.
            if item.name.startswith("_"):
                continue

            # [/absolute/path/to/css]/base.css --> base.css
            # [/absolute/path/to/js]/base.js --> base.js
            # [/absolute/path/to/css]/nested/base.css --> nested/base.css
            # [/absolute/path/to/js]/nested/base.js --> nested/base.js
            yield str(item.relative_to(path))

    def setup(self) -> None:

        action = QAction(aqt.mw)
        action.setText(Defaults.PREFERENCES_MENU_NAME)
        action.setShortcut(Defaults.PREFERENCES_MENU_SHORTCUT)
        action.triggered.connect(self.__preferences_view.show)

        aqt.mw.form.menuTools.addAction(action)  # type: ignore

        def hook__append_assets(
            web_content: WebContent, context: Optional[Any]
        ) -> None:

            if not isinstance(context, (CardLayout, Reviewer)):
                return

            # Add-ons may expose their own web assets by utilizing
            # aqt.addons.AddonManager.setWebExports(). Web exports registered
            # in this manner may then be accessed under the `/_addons` subpath.
            #
            # E.g., to allow access to a `my-addon.js` and `my-addon.css` residing
            # in a "web" subfolder in your add-on package, first register the
            # corresponding web export:
            #
            # > from aqt import mw
            # > mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")

            aqt.mw.addonManager.setWebExports(  # type: ignore
                __name__, fr"{Key.USER_FILES}{os.sep}{Key.ASSETS}{os.sep}.*"
            )

            for css, enabled in self.config.css:

                if enabled is False:
                    continue

                # /_addons/[addon-name]/user_files/assets/css/[relative/path/to/asset].css
                path = str(Defaults.WEB_ASSETS_CSS_PATH / css)

                web_content.css.append(path)

            for js, enabled in self.config.js:

                if enabled is False:
                    continue

                # /_addons/[addon-name]/user_files/assets/js/[relative/path/to/asset].js
                path = str(Defaults.WEB_ASSETS_JS_PATH / js)

                web_content.js.append(path)

        aqt.gui_hooks.webview_will_set_content.append(hook__append_assets)
