from __future__ import annotations

import json
from collections.abc import Iterator

from .helpers import Asset, Extension, Paths


class Config:

    """
    Data structure:
        {
            "css": {
                "base.css": True,
                ...
            },
            "javascript": {
                "base.js": True,
                ...
            }
        }
    """

    __DATA: dict[str, dict[str, bool]] = {
        Asset.CSS.value: {},
        Asset.JAVASCRIPT.value: {},
    }

    _data = __DATA.copy()

    def __init__(self) -> None:
        self._load()

    def toggle_asset(self, asset_type: Asset, name: str) -> None:
        self._data[asset_type.value][name] = not self._data[asset_type.value][name]
        self._write()

    def get_assets(self, asset_type: Asset) -> list[tuple[str, bool]]:
        return sorted(
            self._data[asset_type.value].items(),
            key=lambda t: t[0],
        )

    def _load(self) -> None:

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

        self._validate()

        for asset_type in list(Asset):
            for asset in self._iter_assets(asset_type=asset_type):
                self._data[asset_type.value][asset] = True

    def _update(self):

        self._validate()

        for asset_type in list(Asset):

            # Add new assets.

            new_assets = [
                asset
                for asset in self._iter_assets(asset_type=asset_type)
                if asset not in self._data[asset_type.value]
            ]

            for new_asset in new_assets:
                self._data[asset_type.value][new_asset] = True

            # Remove deleted assets.

            deleted_assets = [
                asset
                for asset in self._data[asset_type.value]
                if asset not in tuple(self._iter_assets(asset_type=asset_type))
            ]

            for deleted_asset in deleted_assets:
                del self._data[asset_type.value][deleted_asset]

    def _write(self, backup=False) -> None:

        path = Paths.ASSETS_JSON if backup is False else Paths.ASSETS_JSON_BAK

        with open(path, "w") as f:
            json.dump(self._data, f, indent=4)

    def _validate(self) -> None:

        try:
            for asset_type in list(Asset):
                self._data[asset_type.value]
        except KeyError:
            self._write(backup=True)
            self._data = self.__DATA.copy()

    @staticmethod
    def _iter_assets(asset_type: Asset) -> Iterator[str]:

        if asset_type == Asset.CSS:
            path = Paths.ASSETS_CSS_ROOT
            extension = Extension.CSS.value
        elif asset_type == Asset.JAVASCRIPT:
            path = Paths.ASSETS_JAVASCRIPT_ROOT
            extension = Extension.JAVASCRIPT.value
        else:
            raise ValueError("invalid value for 'asset_type'")

        # "ext" --> "**/*.ext"
        asset_glob = f"**/*.{extension}"

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

            # [path-to-css]/base.css        --> base.css
            # [path-to-css]/nested/base.css --> nested/base.css
            # [path-to-js]/base.js          --> base.js
            # [path-to-js]/nested/base.js   --> nested/base.js
            yield str(item.relative_to(path))
