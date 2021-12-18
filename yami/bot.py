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

import inspect
import typing

import hikari

from yami import commands as commands_
from yami import context, exceptions

__all__ = ["Bot"]


class Bot(hikari.GatewayBot):
    """A subclass of `hikari.GatewayBot` that provides an interface
    for handling commands.

    This is the class you will instantiate, to utilize command features
    on top of the `hikari.GatewayBot` superclass.

    Args:
        token: str
            The bot token to sign in with.
        prefix: Union[str, Sequence[str]]
            The prefix, or sequence of prefixes to listen for.
            Planned support for mentions, and functions soon (tm).

    Kwargs:
        case_insensitive: bool
            Whether or not to ignore case when handling legacy command
            invocations. Defaults to True.
        owner_ids: Optional[Sequence[int]]
            A sequence of integers representing the Snowflakes of the
            bots owners.
        **kwargs: The remaining kwargs for hikari.GatewayBot.
    """

    __slots__ = (
        "_prefix",
        "_case_insensitive",
        "_owner_ids",
        "_commands",
        "_aliases",
    )

    def __init__(
        self,
        token: str,
        prefix: str | typing.Sequence[str],
        *,
        case_insensitive: bool = True,
        owner_ids: typing.Sequence[int] | None = None,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(token, **kwargs)

        self._prefix: typing.Sequence[str] = (prefix,) if isinstance(prefix, str) else prefix
        self._aliases: dict[str, str] = {}
        self._case_insensitive = case_insensitive
        self._commands: dict[str, commands_.MessageCommand] = {}
        self._owner_ids = owner_ids
        self.subscribe(hikari.MessageCreateEvent, self._listen)

    @property
    def commands(self) -> dict[str, commands_.MessageCommand]:
        """A dictionary of name, MessageCommand pairs associated with
        the bot.
        """
        return self._commands

    @property
    def aliases(self) -> dict[str, str]:
        """A dictionary of aliases to their corresponding
        MessageCommand's name.
        """
        return self._aliases

    def add_command(
        self,
        command: typing.Callable[..., typing.Any] | commands_.MessageCommand,
        *,
        name: str | None = None,
        description: str = "",
        aliases: typing.Iterable[str] = [],
    ) -> commands_.MessageCommand:
        """Adds a command to the bot.

        Args:
            command: Callable[..., Any] | yami.MessageCommand
                The command to add.

        Kwargs:
            name: str | None
                The name of the command (defaults to the function name)
            description: str
                The command descriptions (defaults to "")
            aliases: Iterable[str]
                The command aliases (defaults to [])

        Returns:
            yami.MessageCommand
                The command that was added.

        Raises:
            yami.DuplicateCommand
                If the command shares a name or alias with an existing
                command.
            yami.BadArgument
                If aliases is not a list or a tuple.
        """

        if isinstance(command, commands_.MessageCommand):
            if type(command.aliases) not in (list, tuple):
                raise exceptions.BadArgument(
                    f"Aliases must be a iterable of strings, not: {type(command.aliases)}"
                )

            if command.name in self._commands:
                raise exceptions.DuplicateCommand(
                    f"Failed to add command '{command.name}' - name already in use",
                )

            for a in command.aliases:
                if a in self._aliases:
                    raise exceptions.DuplicateCommand(
                        f"Failed to add command '{command.name}' - alias '{a}' already in use",
                    )

            self._aliases.update(dict((a, command.name) for a in command.aliases))
            self._commands[command.name] = command
            return command

        name = name if name else command.__name__
        cmd = commands_.MessageCommand(command, name, description, aliases)
        return self.add_command(cmd)

    def yield_commands(self) -> typing.Generator[commands_.MessageCommand, None, None]:
        """Yields commands attached to the bot.

        Returns:
            Generator[yami.MessageCommand, ...]
        """
        for cmd in self._commands.values():
            yield cmd

    def get_command(self, name: str, *, alias: bool = False) -> commands_.MessageCommand | None:
        """Gets a command.

        Args:
            name: str
                The name of the command to get.

        Kwargs:
            alias: bool
                Whether or not to search aliases as well as names.
                Defaults to False.

        Returns:
            yami.MessageCommand | None
                The command, or None if not found.
        """
        if alias:
            name = self._aliases.get(name, name)

        return self._commands.get(name)

    def command(
        self,
        name: str | None = None,
        description: str = "",
        *,
        aliases: typing.Iterable[str] = [],
    ) -> typing.Callable[..., typing.Any]:
        """Decorator to add a message command to the bot."""
        return lambda callback: self.add_command(
            commands_.MessageCommand(
                callback,
                name if name else callback.__name__,
                description,
                aliases,
            )
        )

    async def _listen(self, e: hikari.MessageCreateEvent) -> None:
        """Listens for messages."""
        if not e.message.content:
            return

        for p in self._prefix:
            if e.message.content.startswith(p):
                return await self._invoke(p, e, e.message.content)

    async def _invoke(self, p: str, event: hikari.MessageCreateEvent, content: str) -> None:
        """Attempts to invoke a command."""
        parsed = content.split()
        name = parsed.pop(0)[len(p) :]

        # TODO: Fire a CommandInvokeEvent here once we make it

        if name in self._aliases:
            cmd = self._commands[self._aliases[name]]
        elif name in self._commands:
            cmd = self._commands[name]
        else:
            raise exceptions.CommandNotFound(f"No command found with name '{name}'")

        annots = tuple(inspect.get_annotations(cmd.callback).values())
        converted: list[typing.Any] = []

        for i, arg in enumerate(parsed):
            t = annots[i + 1]

            try:
                converted.append(t(arg))
            except (TypeError, ValueError):
                converted.append(arg)

        ctx = context.MessageContext(self, event.message, cmd, p)
        await cmd.callback(ctx, *converted)
