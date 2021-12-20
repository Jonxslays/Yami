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
import typing

from yami import checks as checks_
from yami import exceptions, modules

__all__ = [
    "MessageCommand",
    "command",
]


class MessageCommand:
    """An object that represents a message content command.

    You should not instantiate this class manually, instead use:
    - The `yami.command` decorator inside a `yami.Module` subclass.
    - The `yami.Bot.command` decorator outside a `yami.Module`.
    """

    __slots__ = ("_aliases", "_callback", "_name", "_description", "_module", "_checks")

    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        name: str,
        description: str,
        aliases: typing.Iterable[str],
    ) -> None:
        self._aliases = aliases
        self._callback = callback
        self._description = description
        self._name = name
        self._module: modules.Module | None = None
        self._checks: dict[str, checks_.Check] = {}

    @property
    def aliases(self) -> typing.Iterable[str]:
        """The aliases for the command."""
        return self._aliases

    @property
    def checks(self) -> dict[str, checks_.Check]:
        """A dictionary containing name, Check pairs that are registered
        to this command.
        """
        return self._checks

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

    def add_check(self, check: typing.Type[checks_.Check] | checks_.Check) -> None:
        """Adds a check to be run before this command.

        Args:
            check: `yami.Check`
                The check to add.
        """
        if isinstance(check, checks_.Check):
            self._checks[check.get_name()] = check
        elif isinstance(check, abc.ABCMeta):
            self._checks[check.get_name()] = check()  # type: ignore
        else:
            raise exceptions.CheckAddFailed(
                f"Cannot add {check} to '{self.name}' - it is not a Check"
            )

    def remove_check(self, check: typing.Type[checks_.Check] | checks_.Check) -> None:
        """Removes a check from this command. If this check is not
        bound to this command, it will do nothing.

        Args:
            check: `yami.Check`
                The check to remove.

        Raises:
            `yami.CheckRemovalException`
                When an invalid type is passed as an argument to this
                method.
        """
        if not isinstance(check, (checks_.Check, abc.ABCMeta)):
            raise exceptions.CheckRemovalFailed(
                f"Cannot remove {check} from '{self.name}' - it is not a Check"
            )

        if (name := check.get_name()) in self._checks:
            self._checks.pop(name)

    def yield_checks(self) -> typing.Generator[checks_.Check, None, None]:
        """Yields the checks bound to the command.

        Returns:
            `Generator[yami.Check, ...]`
                A generator over the commands checks.
        """
        yield from self._checks.values()


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
