# Yami - A command handler that complements Hikari.
# Copyright (C) 2021 Jonxslays
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
"""Module containing the Yami converters."""

from __future__ import annotations

import abc
import logging
from typing import Any, Callable, TypeVar

import hikari

from yami import exceptions

__all__ = [
    "HIKARI_CAN_CONVERT",
    "BUILTIN_CAN_CONVERT",
    "Converter",
    "BuiltinConverter",
    "HikariConverter",
]

_log = logging.getLogger(__name__)

BuiltinTypeT = TypeVar("BuiltinTypeT", bound=type)
HikariTypeT = TypeVar("HikariTypeT")

BUILTIN_CAN_CONVERT = (bool, int, complex, float, bytes)
HIKARI_CAN_CONVERT = (
    hikari.User,
    hikari.Member,
    hikari.PartialChannel,
    hikari.GroupDMChannel,
    hikari.GuildTextChannel,
    hikari.GuildVoiceChannel,
    hikari.GuildStoreChannel,
    hikari.GuildNewsChannel,
    hikari.GuildChannel,
    hikari.TextableChannel,
    hikari.Message,
    hikari.Role,
    hikari.CustomEmoji,
    hikari.KnownCustomEmoji,
    hikari.Emoji,
)


class Converter(abc.ABC):
    """Base class all Yami converters inherit from."""

    __slots__ = ()

    def __init__(self, value: Any) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value})"

    def _raise(self, type_: Any) -> exceptions.ConversionFailed:
        return exceptions.ConversionFailed(
            f"Converting to {type_} failed for value: {self._value!r}"
        )


class HikariConverter(Converter):
    """Converts to the hikari types.
    - `hikari.User`
    - `hikari.Member`
    - `hikari.PartialChannel`
    - `hikari.GroupDMChanne'`
    - `hikari.GuildTextChannel`
    - `hikari.GuildVoiceChannel`
    - `hikari.GuildStoreChannel`
    - `hikari.GuildNewsChannel`
    - `hikari.GuildChannel`
    - `hikari.TextableChannel`
    - `hikari.Message`
    - `hikari.Role`
    - `hikari.CustomEmoji`
    - `hikari.KnownCustomEmoji`
    - `hikari.Emoji`
    """

    def __init__(self) -> None:
        raise NotImplementedError("This converter is not yet implemented.")


class BuiltinConverter(Converter):
    """Converts to the builtin types.

    This converter can produce:
    - `bool`
    - `bytes`
    - `int`
    - `complex`
    - `float`
    - `str`

    Args:
        value: `Any`
            The value to perform the conversion on.
    """

    __slots__ = ("_value", "_mapping")

    def __init__(self, value: Any) -> None:
        self._value = value
        self._mapping: dict[type, Callable[..., Any]] = {
            bool: self.as_bool,
            bytes: self.as_bytes,
            complex: self.as_complex,
            float: self.as_float,
            int: self.as_int,
            str: self.as_str,
        }

    @classmethod
    def can_convert(cls, type_: Any) -> bool:
        """Returns `True` if this converter can convert an object to
        type of value passed in.

        Args:
            type_: `Any`
                The type to check compatibility for.

        Returns:
            `bool`
                Whether or not the conversion is possible.
        """
        return type_ in BUILTIN_CAN_CONVERT

    def as_type(self, type_: BuiltinTypeT, *, encoding: str = "utf8") -> BuiltinTypeT:
        """Converts the value to the given type.

        Args:
            type_: `BuiltinTypeT`
                The type to try converting to. Must be one of:
                `bool`, `bytes`, `complex`, `int`, `float`, or `str`.

        Kwargs:
            encoding: `str`
                The encoding if type_ is `bytes`. Defaults to "utf8".

        Raises:
            `yami.ConversionFailed`:
                If the conversion fails for any reason.

        Returns:
            `BuiltinTypeT`:
                The converted value.
        """
        if type_ in self._mapping:
            converted: BuiltinTypeT

            if type_ is bytes:
                converted = self._mapping[type_](encoding)
            else:
                converted = self._mapping[type_]()
            return converted

        raise exceptions.ConversionFailed(f"{self} can't be converted to {type_}")

    def as_bool(self) -> bool:
        """Converts the value to `bool`.
        - 'true' and 'True' with be `True`
        - 'false' and 'False' with be `False`
        """
        if self._value == "true":
            return True
        if self._value == "false":
            return False
        else:
            raise self._raise(bool)

    def as_str(self) -> str:
        """Converts the value to `str`."""
        try:
            return str(self._value)
        except:
            raise self._raise(str) from None

    def as_bytes(self, encoding: str = "utf8") -> bytes:
        """Converts the value to `bytes`.

        Args:
            encoding: `str`
                The encoding to use. Defaults to "utf8".
        """
        try:
            return bytes(self._value, encoding)
        except:
            raise self._raise(bytes) from None

    def as_int(self) -> int:
        """Converts the value to `int`."""
        try:
            return int(self._value)
        except:
            raise self._raise(int) from None

    def as_complex(self) -> complex:
        """Converts to `complex`."""
        try:
            return complex(self._value)
        except:
            raise self._raise(complex) from None

    def as_float(self) -> float:
        """Converts the value to `float`."""
        try:
            return float(self._value)
        except:
            raise self._raise(float) from None
