from __future__ import annotations

import json
from collections.abc import Iterator

from .helpers import Asset, Paths


class Config:
    """A class used to store and mutate the add-on's configuration.

    Three public methods are available: one for toggling an asset's enabled state, one
    for retrieving the all the name and enabled states for a specific asset type, and
    one for reloading the assets from disk.

    The data structure is as follows:

    {
        "css": {
            "card.css": True,
            ...
        },
        "javascript": {
            "card.js": True,
            ...
        }
    }
    """

    __DATA: dict[str, dict[str, bool]] = {
        Asset.CSS.id: {},
        Asset.JAVASCRIPT.id: {},
    }

    _data = __DATA.copy()

    def __init__(self) -> None:
        self._load()

    def toggle_asset(self, asset_type: Asset, name: str) -> None:
        """Toggles an asset with a given type and name."""

        self._data[asset_type.id][name] = not self._data[asset_type.id][name]
        self._write()

    def get_assets(self, asset_type: Asset) -> list[tuple[str, bool]]:
        """Returns all the assets of a give type along with their enabled state."""

        return sorted(
            self._data[asset_type.id].items(),
            key=lambda t: t[0],
        )

    def reload_assets(self) -> None:
        """Loads the assets from disk and updates the configuration."""

        self._update()
        self._write()

    def _load(self) -> None:
        """Loads the add-on's configuration from disk."""

        try:
            with open(Paths.ASSETS_JSON) as f:
                self._data = json.load(f)
        except Exception:
            self._build()
            self._write()
            return

        self._update()
        self._write()

    def _build(self) -> None:
        """Builds the add-on's configuration."""

        self._validate()

        for asset_type in list(Asset):
            for asset in self._iter_assets_directory(asset_type=asset_type):
                self._data[asset_type.id].setdefault(asset, True)

    def _update(self):
        """Updates the add-on's configuration to what's in the assets directory."""

        self._validate()

        for asset_type in list(Asset):

            # Add new assets.

            for asset in self._iter_assets_directory(asset_type=asset_type):
                self._data[asset_type.id].setdefault(asset, True)

            # Remove deleted assets.

            deleted_assets = [
                asset
                for asset in self._data[asset_type.id]
                if asset
                not in tuple(self._iter_assets_directory(asset_type=asset_type))
            ]

            for deleted_asset in deleted_assets:
                del self._data[asset_type.id][deleted_asset]

    def _write(self, backup=False) -> None:
        """Writes the configuration to disk. Optionally writes a back-up instead.

        Args:
            backup: Writes a copy of the configuration with a `.bak` extension. This
                is primarily used when the configuration cannot be read. The current
                version is backed-up and a default configuration is used in its place.
        """

        path = Paths.ASSETS_JSON if backup is False else Paths.ASSETS_JSON_BAK

        with open(path, "w") as f:
            json.dump(self._data, f, indent=4)

    def _validate(self) -> None:
        """Performs a shallow validation of the add-on's config.

        In the case of an error, the current configuration is backed up to disk and the
        default configuration is used in its place.
        """

        try:
            for asset_type in list(Asset):
                self._data[asset_type.id]
        except KeyError:
            self._write(backup=True)
            self._data = self.__DATA.copy()

    @staticmethod
    def _iter_assets_directory(asset_type: Asset) -> Iterator[str]:
        """Iterates through all the assets for a give asset type within the
        `user_files/assets` directory and returns its path relative to the asset's
        respective root directory. For example:

        user_files/assets/css/card.css        --> card.css
        user_files/assets/css/nested/card.css --> nested/card.css
                          ^^^
        CSS root ─────────┘

        user_files/assets/javascript/card.js        --> card.js
        user_files/assets/javascript/nested/card.js --> nested/card.js
                          ^^^^^^^^^^
        JavaScript root ──┘
        """

        path = asset_type.asset_root

        # "ext" --> "**/*.ext"
        asset_glob = f"**/*.{asset_type.extension}"

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

            yield str(item.relative_to(path))
