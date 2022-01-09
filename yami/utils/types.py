# Yami - A command handler that complements Hikari.
# Copyright (C) 2021-present Jonxslays
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

from typing import Any

__all__ = ["Shared", "SharedNone", "YamiNoneType"]


class YamiNoneType(type):
    """Metaclass for `SharedNone`."""

    def __repr__(self) -> str:
        return "SharedNone"

    def __bool__(self) -> bool:
        return False


class SharedNone(object, metaclass=YamiNoneType):
    """The type returned from Shared if an attribute is not set, this
    class can not be instantiated.

    - When a `SharedNone` is returned, it is this class, but its type()
      will be `YamiNoneType`.

    - To check if a value returned by Shared was SharedNone use
      `shared.obj is SharedNone`.
    """

    def __init__(self) -> None:
        raise TypeError(f"{self.__class__.__name__} can not be instantiated.")


class SharedMeta(type):
    """Metaclass for `Shared`."""

    def __repr__(cls) -> str:
        return f"Shared"


class Shared(object, metaclass=SharedMeta):
    """Represents data container for shared storage.

    An instance of `Shared` is stored on each context, and on the bot.

    Feel free to examine this in your own contexts, and even store
    things in one on your bot. You can instantiate a `Shared` anywhere
    you want, in fact.

    You can dynamically add attributes to the shared object.

    .. code-block:: python

        s = yami.Shared()
        s.hello = "hello"
        s.hello # returns "hello"
        s.doesnt_exist # returns yami.SharedNone

    """

    def __getattr__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return SharedNone

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return f"{self.__class__}(items={self.__dict__})"

    def __delattr__(self, name: str) -> None:
        del self.__dict__[name]

    def __del__(self) -> None:
        del self

    @property
    def items(self) -> dict[str, Any]:
        """A dictionary of attribute name, value pairs that have been
        stored inside this `Shared` instance.
        """
        return self.__dict__

    def has(self, name: str) -> bool:
        """Checks whether the `Shared` instance contains an attribute
        with the given name. If so, you can assume the attribute will
        not return a `SharedNone`.

        Args
            name: ``str``
                The name of the attribute to check for.

        Returns
            ``bool``
                `True` if the attribute exists, otherwise `False`.
        """
        return name in self.__dict__
