import json
from typing import TYPE_CHECKING, Dict, List, Tuple

from .helpers import Defaults, E_Asset


if TYPE_CHECKING:
    from .addon import AnkiAssets


class Config:

    """
    Data structure:
        {
            "css": {
                "base.css": True,
                ...
            },
            "js": {
                "base.js": True,
                ...
            }
        }
    """

    __data_default: Dict[str, Dict[str, bool]] = {
        E_Asset.CSS.value: {},
        E_Asset.JS.value: {},
    }

    __data = __data_default.copy()

    def __init__(self, addon: "AnkiAssets"):

        self.__addon = addon
        self.__load()

    def __load(self) -> None:

        try:
            with open(Defaults.ASSETS_JSON, "r") as f:
                self.__data = json.load(f)
        except Exception:
            self.__build()
            self.__save()
            return

        self.__update()
        self.__save()

    def __save(self) -> None:

        with open(Defaults.ASSETS_JSON, "w") as f:
            json.dump(self.__data, f, indent=4)

    def __build(self) -> None:

        self.__check()

        for type in list(E_Asset):
            for asset in self.__addon.assets(type=type):
                self.__data[type.value][asset] = True

    def __update(self):

        self.__check()

        for type in list(E_Asset):

            # Add new assets.

            new_assets = [
                new_asset
                for new_asset in self.__addon.assets(type=type)
                if new_asset not in self.__data[type.value]
            ]

            for new_asset in new_assets:
                self.__data[type.value][new_asset] = True

            # Remove deleted assets.

            deleted_assets = [
                deleted_asset
                for deleted_asset in self.__data[type.value]
                if deleted_asset not in self.__addon.assets(type=type)
            ]

            for deleted_asset in deleted_assets:
                del self.__data[type.value][deleted_asset]

    def __check(self) -> None:

        if self.__data:
            return

        self.__data = self.__data_default.copy()

    def toggle_asset(self, type: E_Asset, name: str) -> None:
        self.__data[type.value][name] = not self.__data[type.value][name]
        self.__save()

    @property
    def css(self) -> List[Tuple[str, bool]]:
        return sorted(
            self.__data[E_Asset.CSS.value].items(),
            key=lambda t: t[0],
        )

    @property
    def js(self) -> List[Tuple[str, bool]]:
        return sorted(
            self.__data[E_Asset.JS.value].items(),
            key=lambda t: t[0],
        )
