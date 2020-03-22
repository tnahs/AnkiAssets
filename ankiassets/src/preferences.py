import functools

import aqt

from .defaults import Asset


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
