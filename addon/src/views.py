from __future__ import annotations

import functools
import textwrap
from typing import Type, TypeVar

from aqt.main import AnkiQt
from aqt.qt.qt6 import (
    QWIDGETSIZE_MAX,
    QCheckBox,
    QDesktopServices,
    QDialog,
    QFont,
    QFontDatabase,
    QGraphicsOpacityEffect,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    Qt,
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
        """Initializes the UI."""

        self.setWindowTitle(Defaults.PREFERENCES_NAME)

        self._font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self._font.setPointSize(12)

        # Asset layouts

        self._layout_css = self._build_asset_layout(asset_type=Asset.CSS)
        self._layout_javascript = self._build_asset_layout(asset_type=Asset.JAVASCRIPT)

        # Info label

        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.5)

        label_info = QLabel(
            "Note that the enabled assets will be loaded for every card."
        )
        label_info.setContentsMargins(0, 15, 0, 15)
        label_info.setWordWrap(True)
        label_info.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label_info.setGraphicsEffect(opacity_effect)

        # Buttons layout

        button_open_assets_folder = QPushButton("Open AnkiAssets Folder...")
        button_open_assets_folder.clicked.connect(self._open_assets_directory)

        button_reload_assets = QPushButton("Reload Assets")
        button_reload_assets.clicked.connect(self._reload_assets)

        button_close = QPushButton("Close")
        button_close.clicked.connect(self.close)
        button_close.setDefault(True)

        layout_buttons = QHBoxLayout()
        layout_buttons.setContentsMargins(0, 0, 0, 0)
        layout_buttons.addWidget(button_open_assets_folder)
        layout_buttons.addSpacing(10)
        layout_buttons.addWidget(button_reload_assets)
        layout_buttons.addSpacing(50)
        layout_buttons.addWidget(button_close)

        # Main layout

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        layout.addLayout(self._layout_css)  # type: ignore
        layout.addSpacing(10)
        layout.addLayout(self._layout_javascript)  # type: ignore
        layout.addWidget(label_info)
        layout.addLayout(layout_buttons)

        self.setLayout(layout)

    def _rebuild_asset_layouts(self) -> None:
        """Rebuilds the asset layouts."""

        self._clear_layout(self._layout_css)
        self._build_asset_layout(
            asset_type=Asset.CSS,
            layout=self._layout_css,
        )

        self._clear_layout(self._layout_javascript)
        self._build_asset_layout(
            asset_type=Asset.JAVASCRIPT,
            layout=self._layout_javascript,
        )

    def _build_asset_layout(
        self, asset_type: Asset, layout: QVBoxLayout | None = None
    ) -> QVBoxLayout | None:
        """Builds an asset layout given an optional `QVBoxLayout`.

        An asset layout looks like the following:

        ┌╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴─┐
        ╷   AssetLabel:                             ╷
        ╷ ┌───────────────────────────────────────┐ ╷
        ╷ │  ■ card.ext                           │ ╷
        ╷ │  ■ field.ext                          │ ╷
        ╷ │  □ ...                                │ ╷
        ╷ └───────────────────────────────────────┘ ╷
        └╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴╴─┘
        """

        assets = self._config.get_assets(asset_type=asset_type)

        label = QLabel(f"{asset_type.label}:")
        label.setContentsMargins(5, 0, 0, 5)

        layout_checkboxes = QVBoxLayout()
        layout_checkboxes.setContentsMargins(15, 15, 15, 15)
        layout_checkboxes.setSpacing(10)

        # Create a checkbox for each asset...
        if assets:

            for name, state in assets:

                checkbox = QCheckBox(name)
                checkbox.setChecked(state)
                checkbox.setFont(self._font)
                checkbox.toggled.connect(
                    functools.partial(
                        self._config.toggle_asset, asset_type=asset_type, name=name
                    )
                )

                layout_checkboxes.addWidget(checkbox)

        # ...or display a message if no assets are found.
        else:

            opacity_effect = QGraphicsOpacityEffect()
            opacity_effect.setOpacity(0.25)

            label_no_assets = QLabel(f"No {asset_type.label} assets found...")
            label_no_assets.setGraphicsEffect(opacity_effect)

            layout_checkboxes.addWidget(label_no_assets)

        group = QGroupBox()
        group.setLayout(layout_checkboxes)

        # Mutate the layout if one is provided, otherwise create a new layout.
        layout_ = layout if layout is not None else QVBoxLayout()
        layout_.setContentsMargins(0, 0, 0, 0)
        layout_.addWidget(label)
        layout_.addWidget(group)

        if layout is None:
            return layout_

    def _clear_layout(self, layout: QVBoxLayout | None) -> None:
        """Clears all widgets and layouts from a layout."""

        if layout is not None:

            while layout.count():

                item = layout.takeAt(0)
                widget = item.widget()

                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())  # type: ignore

    def _reload_assets(self) -> None:
        """Reloads the assets and rebuilds the UI."""

        self._config.reload_assets()
        self._rebuild_asset_layouts()

    @staticmethod
    def _open_assets_directory() -> None:
        """Opens the root assets directory. Creates it if it doesn't exist."""

        Paths.ASSETS_ROOT.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl(f"file:///{Paths.ASSETS_ROOT}"))
