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

import asyncio
import typing

from yami import exceptions, modules

__all__ = [
    "MessageCommand",
    "command",
]


class MessageCommand:
    """An object that represents a message content command. You should
    not instantiate this class manually, instead use the `yami.command`
    or `yami.Bot.command` decorator.

    Args:
        callback: Callable[..., Any]
            The callback to run when the command is invoked.
        name: str
            The name of the command.
        descriptions: str
            The commands description.
        aliases: Iterable[str]
            The aliases to use for the command.
    """

    __slots__ = (
        "_aliases",
        "_callback",
        "_name",
        "_description",
        "_module",
    )

    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        name: str,
        description: str,
        aliases: typing.Iterable[str],
        module: modules.Module | None = None,
    ) -> None:
        self._aliases = aliases
        self._callback = callback
        self._description = description
        self._name = name
        self._module = module

        if not asyncio.iscoroutinefunction(callback):
            raise exceptions.AsyncRequired(
                f"Command callbacks must be asynchronous: function {callback}"
            )

    @property
    def aliases(self) -> typing.Iterable[str]:
        """The aliases for the command.

        Returns:
            Iterable[str]
                The aliases for the command or an empty list if there
                are none.
        """
        return self._aliases

    @property
    def name(self) -> str:
        """The name of the command."""
        return self._name

    @property
    def module(self) -> modules.Module | None:
        """The module this command originates from, if any."""
        return self._module

    @property
    def description(self) -> str:
        """The commands description."""
        return self._description

    @property
    def callback(self) -> typing.Callable[..., typing.Any]:
        """The callback function registered to the command."""
        return self._callback


def command(
    name: str | None = None,
    description: str = "",
    *,
    aliases: typing.Iterable[str] = [],
) -> typing.Callable[..., MessageCommand]:
    """Decorator to add commands to the bot inside of modules. It should
    decorate the callback that should fire when this command is run.

    Args:
        name: str
            The name of the command. Defaults to the function name.
        description: str
            The command description. If omitted, the callbacks docstring
            will be used instead. REMINDER: docstrings are stripped from
            your programs bytecode when it is run with the `-OO`
            optimization flag.

    Kwargs:
        aliases: Iterable[str]
            A list or tuple of aliases for the command.

    Returns:
        Callable[..., yami.MessageCommand]
            The callback, but transformed into a message command.
    """
    return lambda callback: MessageCommand(
        callback,
        name or callback.__name__,
        description or callback.__doc__,
        aliases,
    )
