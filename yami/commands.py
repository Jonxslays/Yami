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
"""Module containing all Command related objects."""

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

    __slots__ = (
        "_aliases",
        "_callback",
        "_name",
        "_description",
        "_module",
        "_checks",
        "_was_globally_added",
        "_raise_conversion",
        "_subcommands",
        "_parent",
        "_invoke_with",
    )

    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        name: str,
        description: str,
        *,
        aliases: typing.Iterable[str],
        raise_conversion: bool,
        parent: MessageCommand | None = None,
        invoke_with: bool = False,
    ) -> None:
        self._name = name
        self._aliases = aliases
        self._callback = callback
        self._description = description
        self._invoke_with = invoke_with
        self._parent = parent
        self._raise_conversion = raise_conversion
        self._module: modules.Module | None = None
        self._checks: dict[str, checks_.Check] = {}
        self._subcommands: dict[str, MessageCommand] = {}
        self._was_globally_added = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._name}')"

    @property
    def aliases(self) -> typing.Iterable[str]:
        """The aliases for the command."""
        return self._aliases

    @property
    def checks(self) -> dict[str, checks_.Check]:
        """A dictionary containing name, `yami.Check` pairs that are
        registered to this command.
        """
        return self._checks

    @property
    def name(self) -> str:
        """The name of the command."""
        return self._name

    @property
    def module(self) -> modules.Module | None:
        """The `yami.Module` this command originates from, if any."""
        return self._module

    @property
    def description(self) -> str:
        """The commands description."""
        return self._description

    @property
    def callback(self) -> typing.Callable[..., typing.Any]:
        """The callback function registered to the command."""
        return self._callback

    @property
    def raise_conversion(self) -> bool:
        """Whether or not to raise an error when a type hint conversion
        for the command arguments fails.
        """
        return self._raise_conversion

    @property
    def was_globally_added(self) -> bool:
        """`True` if the command was created with the `yami.command`
        decorator. `False` if `yami.Bot.command` was used.
        """
        return self._was_globally_added

    @was_globally_added.setter
    def was_globally_added(self, val: bool) -> None:
        self._was_globally_added = val

    @property
    def subcommands(self) -> dict[str, MessageCommand]:
        """A dictionary containing name, `yami.MessageCommand` pairs
        that are registered to this command.
        """
        return self._subcommands

    @property
    def is_subcommand(self) -> bool:
        """Whether or not this command is a subcommand."""
        return self._parent is not None

    @property
    def parent(self) -> MessageCommand | None:
        """The parent of this command, or `None` if this command is not
        a subcommand.
        """
        return self._parent

    @property
    def invoke_with(self) -> bool:
        """Whether or not to invoke this command if one of it's
        subcommands are invoked.
        """
        return self._invoke_with

    def add_check(self, check: typing.Type[checks_.Check] | checks_.Check) -> checks_.Check:
        """Adds a check to be run before this command.

        Args:
            check: `yami.Check`
                The check to add.

        Returns:
            `yami.Check`
                The check that was added.

        Raises:
            `yami.CheckAddFailed`
                If the check is not a `Check` object.
        """
        try:
            if isinstance(check, checks_.Check):
                value = check
            else:
                value = check()
        except Exception:
            raise exceptions.CheckAddFailed(
                f"Cannot add {check} to '{self.name}' - it is not a Check"
            )

        self._checks[value.get_name()] = value
        return value

    def remove_check(
        self, check: typing.Type[checks_.Check] | checks_.Check
    ) -> checks_.Check | None:
        """Removes a check from this command. If this check is not
        bound to this command, it will do nothing.

        Args:
            check: `yami.Check`
                The check to remove.

        Raises:
            `yami.CheckRemovalFailed`
                When an invalid type is passed as an argument to this
                method.
        """
        if not isinstance(check, (checks_.Check, abc.ABCMeta)):
            raise exceptions.CheckRemovalFailed(
                f"Cannot remove {check} from '{self.name}' - it is not a Check"
            )

        if (name := check.get_name()) in self._checks:
            return self._checks.pop(name)

        return None

    def add_subcommand(
        self,
        command: typing.Callable[..., typing.Any] | MessageCommand,
        *,
        name: str | None = None,
        description: str = "",
        aliases: list[str] | tuple[str, ...] = [],
        raise_conversion: bool = False,
    ) -> MessageCommand:
        """Adds a subcommand to the command.

        Args:
            command: `Callable[..., Any]` | `yami.MessageCommand`
                The subcommand to add.

        Kwargs:
            name: `str` | `None`
                The name of the subcommand
                (defaults to the function name)
            description: `str`
                The subcommands description (defaults to "")
            aliases: `Iterable[str]`
                The subcommands aliases (defaults to [])

        Returns:
            `yami.MessageCommand`
                The subcommand that was added.

        Raises:
            `yami.DuplicateCommand`
                If the subcommand shares a name or alias with an
                existing subcommand.
            `TypeError`
                If aliases is not a list or a tuple.
        """
        if isinstance(command, MessageCommand):
            if not isinstance(command.aliases, (list, tuple)):
                raise TypeError(
                    f"Aliases must be a iterable of strings, not: {type(command.aliases)}"
                )

            if command.name in self._subcommands:
                raise exceptions.DuplicateCommand(
                    f"Failed to add subcommand {command} to {self} - name already in use"
                )

            for alias in filter(
                lambda a: a in (sa.aliases for sa in self.iter_subcommands()), command.aliases
            ):
                raise exceptions.DuplicateCommand(
                    f"Failed to add subcommand {command} to {self} "
                    f"- alias {alias!r} already in use"
                )

            self._subcommands[command.name] = command
            return command

        cmd = MessageCommand(
            command,
            name or command.__name__,
            description,
            aliases=aliases,
            raise_conversion=raise_conversion,
            parent=self,
        )
        return self.add_subcommand(cmd)

    def iter_checks(self) -> typing.Iterator[checks_.Check]:
        """Returns an iterator over the checks bound to the command.

        Returns
            :obj:`~typing.Iterator` [:obj:`~yami.Check`, ...]
                An iterator over the commands checks.
        """
        yield from self._checks.values()

    def iter_subcommands(self) -> typing.Generator[MessageCommand, None, None]:
        """Returns an iterator over the subcommands registered to the
        command.

        Returns
            :obj:`~typing.Iterator` [:obj:`~MessageCommand`, ...]
                An iterator over the commands subcommands.
        """
        yield from self._subcommands.values()

    def subcommand(
        self,
        name: str | None = None,
        description: str = "",
        *,
        aliases: typing.Iterable[str] = [],
        raise_conversion: bool = False,
        invoke_with: bool = False,
    ) -> typing.Callable[..., MessageCommand]:
        """Decorator to add a subcommand to an existing command. It
        should decorate the callback that should fire when this
        subcommand is run.

        Args:
        -----
        - **name**: `str`
            The name of the subcommand. Defaults to the function name.
        - **description**: `str`
            The subcommand description. If omitted, the callbacks
            docstring will be used instead.

        Kwargs:
        -------
        - **aliases**: `Iterable[str]`
            A list or tuple of aliases for the command.
        - **raise_conversion**: `bool`
            Whether or not to raise `yami.ConversionFailed` when
            converting a command argument fails.
        - **invoke_with**: `bool`
            Whether or not to invoke this commands callback, when its
            subcommand is invoked.

        Returns:
        --------
        - `Callable[..., MessageCommand]`
            The callback, but transformed into a MessageCommand.
        """
        return lambda callback: self.add_subcommand(
            MessageCommand(
                callback,
                name or callback.__name__,
                description or callback.__doc__ or "",
                aliases=aliases,
                raise_conversion=raise_conversion,
                invoke_with=invoke_with,
                parent=self,
            )
        )


def command(
    name: str | None = None,
    description: str = "",
    *,
    aliases: typing.Iterable[str] = [],
    raise_conversion: bool = False,
    invoke_with: bool = False,
) -> typing.Callable[..., MessageCommand]:
    """Decorator to add commands to the bot inside of modules. It should
    decorate the callback that should fire when this command is run.

    Args
        - name: `str`
            The name of the command. Defaults to the function name.
        - description: `str`
            The command description. If omitted, the callbacks docstring
            will be used instead.

    Kwargs
        - aliases: ``Iterable[str]``
            A list or tuple of aliases for the command.
        - raise_conversion: ``bool``
            Whether or not to raise `yami.ConversionFailed` when
            converting a command argument fails.
        - invoke_with: ``bool``
            Whether or not to invoke this commands callback, when its
            subcommand is invoked.

    Returns
        ``Callable[..., :obj:`yami.MessageCommand`]``
            The callback, but transformed into a message command.
    """
    return lambda callback: MessageCommand(
        callback,
        name or callback.__name__,
        description or callback.__doc__ or "",
        aliases=aliases,
        raise_conversion=raise_conversion,
        invoke_with=invoke_with,
    )
