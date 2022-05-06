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
"""Module containing the Yami converters."""

from __future__ import annotations

import abc
import logging
from typing import Any, Callable, TypeVar

import hikari

from yami import exceptions

__all__ = [
    "Converter",
    "BuiltinConverter",
    "HikariConverter",
    "HIKARI_CAN_CONVERT",
    "BUILTIN_CAN_CONVERT",
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
    hikari.GuildStageChannel,
    hikari.GuildCategory,
    hikari.GuildNewsChannel,
    hikari.GuildChannel,
    hikari.TextableChannel,
    hikari.TextableGuildChannel,
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

    .. warning::

        Not yet implemented!
    """

    def __init__(self) -> None:
        raise NotImplementedError("This converter is not yet implemented.")


class BuiltinConverter(Converter):
    """Converts to the builtin types.

    Args:
        value (:obj:`~typing.Any`)
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
        """Whether or not this converter can convert an object to this
        type.

        Args:
            type_ (:obj:`~typing.Any`): The type to check compatibility
                for.

        Returns:
            :obj:`bool`: ``True`` if it can be converted.
        """
        return type_ in BUILTIN_CAN_CONVERT

    def as_type(self, type_: BuiltinTypeT, *, encoding: str = "utf8") -> BuiltinTypeT:
        """Converts the value to the given type.

        Args:
            type_ (:obj:`BuiltinTypeT`): The type to try converting to.

        Keyword Args:
            encoding (:obj:`str`): The encoding if ``type_`` is
                :obj:`bytes`. Defaults to ``"utf8"``.

        Returns:
            :obj:`BuiltinTypeT`: The converted value.

        Raises:
            `~yami.ConversionFailed`: If the conversion fails for any
                reason.
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
        """Converts the value to :obj:`bool`.

        .. hint::
            - ``'true'`` and ``'True'`` will be ``True``
            - ``'false'`` and ``'False'`` will be ``False``

        Returns:
            :obj:`bool`: The converted value.

        Raises:
            `~yami.ConversionFailed`: If the conversion fails for any
                reason.
        """
        if self._value == "true":
            return True
        if self._value == "false":
            return False
        else:
            raise self._raise(bool)

    def as_str(self) -> str:
        """Converts the value to :obj:`str`.

        Returns:
            :obj:`str`: The converted value.

        Raises:
            `~yami.ConversionFailed`: If the conversion fails for any
                reason.
        """
        try:
            return str(self._value)
        except:
            raise self._raise(str) from None

    def as_bytes(self, encoding: str = "utf8") -> bytes:
        """Converts the value to :obj:`bytes`.

        Args:
            encoding (:obj:`str`): The encoding to use. Defaults to
                ``"utf8"``.

        Returns:
            :obj:`bytes`: The converted value.

        Raises:
            `~yami.ConversionFailed`: If the conversion fails for any
                reason.
        """
        try:
            return bytes(self._value, encoding)
        except:
            raise self._raise(bytes) from None

    def as_int(self) -> int:
        """Converts the value to :obj:`int`.

        Returns:
            :obj:`int`: The converted value.

        Raises:
            `~yami.ConversionFailed`: If the conversion fails for any
                reason.
        """
        try:
            return int(self._value)
        except:
            raise self._raise(int) from None

    def as_complex(self) -> complex:
        """Converts to :obj:`complex`.

        Returns:
            :obj:`complex`: The converted value.

        Raises:
            `~yami.ConversionFailed`: If the conversion fails for any
                reason.
        """
        try:
            return complex(self._value)
        except:
            raise self._raise(complex) from None

    def as_float(self) -> float:
        """Converts the value to :obj:`float`.

        Returns:
            :obj:`float`: The converted value.

        Raises:
            `~yami.ConversionFailed`: If the conversion fails for any
                reason.
        """
        try:
            return float(self._value)
        except:
            raise self._raise(float) from None
