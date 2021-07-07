import functools
from typing import TYPE_CHECKING, Optional

from aqt.main import AnkiQt
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QFontDatabase
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
)

from .helpers import Defaults, E_Asset


if TYPE_CHECKING:
    from .addon import AnkiAssets


class PreferencesView(QDialog):
    def __init__(self, addon: "AnkiAssets", parent: Optional[AnkiQt]) -> None:
        super().__init__(parent)

        self.__addon = addon
        self.__init_ui()

    def __init_ui(self) -> None:

        self.setWindowTitle(Defaults.PREFERENCES_NAME)

        font__monospace = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font__monospace.setPointSize(14)

        # CSS

        layout__css = QVBoxLayout()
        layout__css.setContentsMargins(12, 10, 10, 10)
        layout__css.setSpacing(5)

        for name, state in self.__addon.config.css:

            checkbox = QCheckBox(f"css/{name}")
            checkbox.setFont(font__monospace)
            checkbox.setChecked(state)
            checkbox.toggled.connect(
                functools.partial(
                    self.__addon.config.toggle_asset,
                    type=E_Asset.CSS,
                    name=name,
                )
            )

            layout__css.addWidget(checkbox)

        group__css = QGroupBox("CSS:")
        group__css.setLayout(layout__css)
        group__css.setFont(font__monospace)

        # JS

        layout__js = QVBoxLayout()
        layout__js.setContentsMargins(12, 10, 10, 10)
        layout__js.setSpacing(5)

        for name, state in self.__addon.config.js:

            checkbox = QCheckBox(f"js/{name}")
            checkbox.setFont(font__monospace)
            checkbox.setChecked(state)
            checkbox.toggled.connect(
                functools.partial(
                    self.__addon.config.toggle_asset,
                    type=E_Asset.JS,
                    name=name,
                )
            )

            layout__js.addWidget(checkbox)

        group__js = QGroupBox("JS:")
        group__js.setLayout(layout__js)
        group__js.setFont(font__monospace)

        # Buttons

        button__open_assets_folder = QPushButton("Open AnkiAssets Folder...")
        button__open_assets_folder.clicked.connect(
            functools.partial(
                QDesktopServices.openUrl,
                QUrl(f"file:///{Defaults.ASSETS}"),
            )
        )

        button__close = QPushButton("Close")
        button__close.clicked.connect(self.close)

        layout__buttons = QHBoxLayout()
        layout__buttons.addWidget(button__open_assets_folder)
        layout__buttons.addStretch()
        layout__buttons.addWidget(button__close)

        # Main Layout

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(group__css)
        layout.addSpacing(10)
        layout.addWidget(group__js)
        layout.addSpacing(15)
        layout.addLayout(layout__buttons)

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
