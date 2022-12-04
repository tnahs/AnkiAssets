from __future__ import annotations

import os

import aqt
import aqt.gui_hooks
from aqt.browser.previewer import BrowserPreviewer
from aqt.clayout import CardLayout
from aqt.qt.qt6 import QAction
from aqt.reviewer import Reviewer
from aqt.webview import WebContent

from .config import Config
from .helpers import Asset, Defaults, Key, Paths
from .views import PreferencesView


class AnkiAssets:
    def __init__(self) -> None:
        self._config = Config()
        self._preferences_view = PreferencesView(config=self._config, parent=aqt.mw)

    def setup(self) -> None:

        if aqt.mw is None:
            return

        action = QAction(aqt.mw)
        action.setText(Defaults.PREFERENCES_MENU_NAME)
        action.setShortcut(Defaults.PREFERENCES_MENU_SHORTCUT)
        action.triggered.connect(self._preferences_view.show)

        aqt.mw.form.menuTools.addAction(action)

        def hook__append_assets(
            web_content: WebContent, context: object | None
        ) -> None:

            if aqt.mw is None:
                return

            if not isinstance(context, (BrowserPreviewer, CardLayout, Reviewer)):
                return

            # Add-ons may expose their own web assets by utilizing
            # aqt.addons.AddonManager.setWebExports(). Web exports registered
            # in this manner may then be accessed under the `/_addons` subpath.
            #
            # E.g., to allow access to a `my-addon.js` and `my-addon.css`
            # residing in a "web" subfolder in your add-on package, first
            # register the corresponding web export:
            #
            # > from aqt import mw
            # > mw.addonManager.setWebExports(__name__, r"web/.*(css|js)")

            aqt.mw.addonManager.setWebExports(
                __name__, rf"{Key.USER_FILES}{os.sep}{Key.ASSETS}{os.sep}.*"
            )

            for css, enabled in self._config.get_assets(Asset.CSS):

                if enabled is False:
                    continue

                # /_addons/[addon-name]/user_files/assets/css/asset.css
                path = str(Paths.WEB_ASSETS_CSS_ROOT / css)

                web_content.css.append(path)

            for javascript, enabled in self._config.get_assets(Asset.JAVASCRIPT):

                if enabled is False:
                    continue

                # /_addons/[addon-name]/user_files/assets/javascript/asset.js
                path = str(Paths.WEB_ASSETS_JAVASCRIPT_ROOT / javascript)

                web_content.js.append(path)

        aqt.gui_hooks.webview_will_set_content.append(hook__append_assets)
