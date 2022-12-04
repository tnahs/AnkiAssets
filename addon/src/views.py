from __future__ import annotations

import functools

from aqt.main import AnkiQt
from aqt.qt.qt6 import (
    QCheckBox,
    QDesktopServices,
    QDialog,
    QFontDatabase,
    QGraphicsOpacityEffect,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QUrl,
    QVBoxLayout,
)

from .config import Config
from .helpers import Asset, Defaults, Paths


class PreferencesView(QDialog):
    def __init__(self, config: Config, parent: AnkiQt | None) -> None:
        super().__init__(parent)

        self._config = config
        self._init_ui()

    def _init_ui(self) -> None:

        self.setWindowTitle(Defaults.PREFERENCES_NAME)

        font_monospace = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font_monospace.setPointSize(12)

        # CSS

        layout_css = QVBoxLayout()
        layout_css.setContentsMargins(12, 10, 10, 10)
        layout_css.setSpacing(15)

        css_assets = self._config.get_assets(asset_type=Asset.CSS)

        if not css_assets:

            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.25)

            label_css = QLabel("No CSS loaded...")
            label_css.setGraphicsEffect(effect)

            layout_css.addWidget(label_css)

        else:

            for name, state in css_assets:

                checkbox = QCheckBox(name)
                checkbox.setFont(font_monospace)
                checkbox.setChecked(state)
                checkbox.toggled.connect(
                    functools.partial(
                        self._config.toggle_asset,
                        asset_type=Asset.CSS,
                        name=name,
                    )
                )

                layout_css.addWidget(checkbox)

        group_css = QGroupBox("CSS:")
        group_css.setLayout(layout_css)

        # JavaScript

        layout_javascript = QVBoxLayout()
        layout_javascript.setContentsMargins(12, 10, 10, 10)
        layout_javascript.setSpacing(5)

        javascript_assets = self._config.get_assets(asset_type=Asset.JAVASCRIPT)

        if not javascript_assets:

            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.25)

            label_javascript = QLabel("No JavaScript loaded...")
            label_javascript.setGraphicsEffect(effect)

            layout_javascript.addWidget(label_javascript)

        else:

            for name, state in javascript_assets:

                checkbox = QCheckBox(name)
                checkbox.setFont(font_monospace)
                checkbox.setChecked(state)
                checkbox.toggled.connect(
                    functools.partial(
                        self._config.toggle_asset,
                        asset_type=Asset.JAVASCRIPT,
                        name=name,
                    )
                )

                layout_javascript.addWidget(checkbox)

        group_javascript = QGroupBox("JavaScript:")
        group_javascript.setLayout(layout_javascript)

        # Buttons

        button_open_assets_folder = QPushButton("Open AnkiAssets Folder...")
        button_open_assets_folder.clicked.connect(
            functools.partial(
                QDesktopServices.openUrl,
                QUrl(f"file:///{Paths.ASSETS_ROOT}"),
            )
        )

        button_close = QPushButton("Close")
        button_close.clicked.connect(self.close)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(button_open_assets_folder)
        layout_buttons.addStretch()
        layout_buttons.addWidget(button_close)

        # Main Layout

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(group_css)
        layout.addSpacing(10)
        layout.addWidget(group_javascript)
        layout.addSpacing(15)
        layout.addLayout(layout_buttons)

        self.setLayout(layout)
        self.setStyleSheet(
            """
            QPushButton {
                padding: 5px 10px;
            }
            """
        )

    def show(self):
        super().show()

        height = self.size().height()
        width = (
            Defaults.PREFERENCES_MINIMUM_WIDTH
            if self.size().width() < Defaults.PREFERENCES_MINIMUM_WIDTH
            else self.size().width()
        )

        self.setFixedSize(width, height)
