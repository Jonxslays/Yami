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

from __future__ import annotations

import abc
import logging
from typing import Any

import hikari

from yami import exceptions

__all__ = ["HIKARI_CAN_CONVERT", "BUILTIN_CAN_CONVERT", "Converter", "BuiltinConverter"]

_log = logging.getLogger(__name__)


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

    def _raise(self, convert: Any) -> exceptions.ConversionFailed:
        return exceptions.ConversionFailed(
            f"Converting to {convert} failed for value: {self._value!r}"
        )


class BuiltinConverter(Converter):
    """Converts to the builtin types.
    - `bool`
    - `bytes`
    - `int`
    - `complex`
    - `float`
    - `str`
    """

    __slots__ = ("_value", "_mapping")

    def __init__(self, value: Any) -> None:
        self._value = value
        self._mapping = {
            bool: self.to_bool,
            bytes: self.to_bytes,
            complex: self.to_complex,
            float: self.to_float,
            int: self.to_int,
            str: self.to_str,
        }

    @classmethod
    def can_convert(cls, value: Any) -> bool:
        """Returns `True` if this converter can convert an object to
        type of value passed in.

        Args:
            value: `Any`
                The type to check compatibility for.

        Returns:
            `bool`
                Whether or not the conversion is possible.
        """
        return value in BUILTIN_CAN_CONVERT

    def from_type(self, value: Any, *, encoding: str = "utf8") -> Any:
        """Converts to the type of value passed to this method.

        Args:
            value: `Any`
                The type to try converting to.

        Kwargs:
            encoding: `str`
                The encoding if value is bytes. Defaults to 'utf8'.

        Raises:
            `yami.ConversionFailed`:
                If the conversion fails for any reason.

        Returns:
            `Any`:
                The converted value.
        """
        if value in self._mapping:
            if value is bytes:
                return bytes(self._value, encoding)

            return self._mapping[value]()  # type: ignore

        raise exceptions.ConversionFailed(f"Can't convert {self} to {value} - it's not a builtin")

    def to_bool(self) -> bool:
        """Converts to `bool`.
        - 'true' and 'True' with be `True`
        - 'false' and 'False' with be `False`
        """
        if self._value == "true":
            return True
        if self._value == "false":
            return False
        else:
            raise self._raise(bool)

    def to_str(self) -> str:
        """Converts to `str`."""
        try:
            return str(self._value)
        except:
            raise self._raise(str) from None

    def to_bytes(self, encoding: str = "utf8") -> bytes:
        """Converts to bytes.

        Args:
            encoding: `str`
                The encoding to use. Defaults to 'utf8'.
        """
        try:
            return bytes(self._value, encoding)
        except:
            raise self._raise(bytes) from None

    def to_int(self) -> int:
        """Converts to `int`."""
        try:
            return int(self._value)
        except:
            raise self._raise(int) from None

    def to_complex(self) -> complex:
        """Converts to `complex`."""
        try:
            return complex(self._value)
        except:
            raise self._raise(complex) from None

    def to_float(self) -> float:
        """Converts to `float`."""
        try:
            return float(self._value)
        except:
            raise self._raise(float) from None
