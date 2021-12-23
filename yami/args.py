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
"""Classes representing command arguments."""

from __future__ import annotations

import inspect
import logging
from typing import TYPE_CHECKING, Any

from yami import converters, exceptions

if TYPE_CHECKING:
    from yami import context

__all__ = ["MessageArg"]

_log = logging.getLogger(__name__)


class MessageArg:
    """Represents a MessageCommand argument."""

    __slots__ = ("_param", "_name", "_kind", "_is_empty", "_annotation", "_is_converted", "_value")

    def __init__(self, param: inspect.Parameter, value: str) -> None:
        self._value: Any = value
        self._param = param
        self._name = param.name
        self._kind = param.kind
        self._annotation = param.annotation
        self._is_converted = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._name}: {type(self._value)})"

    @property
    def name(self) -> str:
        """The name of this arg as it appears in the callback."""
        return self._name

    @property
    def value(self) -> Any:
        """Returns the converted value, or the raw string value if no
        conversion occurred."""
        return self._value

    @property
    def annotation(self) -> Any:
        """The annotations for this arg."""
        return self._annotation

    @property
    def kind(self) -> inspect._ParameterKind:
        """The parameter kind this is."""
        return self._kind

    @property
    def is_empty(self) -> bool:
        """Returned `True` if the argument had not type hints."""
        return self._annotation is inspect.Signature.empty

    @property
    def is_converted(self) -> bool:
        """Whether or not this argument has been converted yet."""
        return self._is_converted

    def _raise(self, ctx: context.MessageContext) -> None:
        raise exceptions.ConversionFailed(
            f"Failed to convert arg {self._name!r} for {ctx.command}"
        )

    async def convert(self, ctx: context.MessageContext) -> None:
        _log.debug(f"Attempting conversion of message arg {self._name!r} to {self._annotation}")

        if self._annotation in converters.BUILTIN_CAN_CONVERT:
            return await self._convert_builtin(ctx)

        return ctx.args.append(self)

    async def _convert_builtin(self, ctx: context.MessageContext) -> None:
        converter = converters.BuiltinConverter(self._value)

        try:
            self._value = converter.as_type(self._annotation)
        except exceptions.ConversionFailed:
            return self._raise(ctx)

        self._is_converted = True
        ctx.args.append(self)
