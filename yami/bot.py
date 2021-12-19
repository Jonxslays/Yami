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

import builtins
import importlib
import inspect
import os
import typing
from pathlib import Path

import hikari

from yami import commands as commands_
from yami import context, exceptions
from yami import modules as modules_

__all__ = ["Bot"]


class Bot(hikari.GatewayBot):
    """A subclass of `hikari.GatewayBot` that provides an interface
    for handling commands.

    This is the class you will instantiate, to utilize command features
    on top of the `hikari.GatewayBot` superclass.

    NOTE: This class is slotted, if you want to set your own custom
    properties you will need to subclass it. Remember to add `__slots__`
    to your subclass so you can take advantage of the performance
    increase!

    Args:
        token: str
            The bot token to sign in with.
        prefix: Union[str, Sequence[str]]
            The prefix, or sequence of prefixes to listen for.
            Planned support for mentions, and functions soon (tm).

    Kwargs:
        case_insensitive: bool
            Whether or not to ignore case when handling message command
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
        "_modules",
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
        self._modules: dict[str, modules_.Module] = {}

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

    @property
    def modules(self) -> dict[str, modules_.Module]:
        """A dictionary of name, `Module` pairs that are synced to the
        bot.
        """
        return self._modules

    def load_modules(self, *paths: str | Path, recursive: bool = True) -> None:
        """Loads all modules from each of the given relative filepaths.
        This method looks for all `.py` files that do not begin with an
        `_`. It is recursive by default.

        Args:
            *paths: `str` | `pathlib.Path`
                One or multiple paths to load modules from.
        """
        for p in paths:
            if not isinstance(p, Path):
                p = Path(os.path.relpath(p))

            for file in filter(
                lambda m: not m.stem.startswith("_"),
                (p.rglob("*.py") if recursive else p.glob("*.py")),
            ):
                container = importlib.import_module(str(file).replace(".py", "").replace("/", "."))

                for mod in filter(
                    lambda m: inspect.isclass(m) and issubclass(m, modules_.Module),
                    container.__dict__.values(),
                ):
                    self.add_module(mod(self))

    def add_module(self, module: modules_.Module) -> None:
        """Adds a `yami.Module` to the bot.

        Args:
            module: `yami.Module`
                The module to add to the bot.

        Raises:
            `ValueError`
                When a module with the same name is already added to the
                bot.
        """
        if module.name in self._modules:
            raise ValueError(
                f"Failed to add module, a module with name '{module.name}' already exists"
            )

        cmd_buf = self._commands.copy()
        for cmd in module.commands.values():
            try:
                self.add_command(cmd)
            except exceptions.YamiException:
                self._commands = cmd_buf
                raise exceptions.ModuleLoadException(
                    f"Failed to load module {module} due to command '{cmd.name}'"
                )

        self._modules[module.name] = module
        module._loaded = True

    def remove_module(self, name: str) -> modules_.Module:
        """Removes a module from the bot.

        Args:
            name: str
                The name of the module to remove.

        Returns:
            yami.Module
                The module that was remove.

        Raises:
            ValueError
                When no module with this name is found on the bot.
        """
        if name in self._modules:
            module = self._modules.get(name)
            assert module is not None
            commands = module.commands.copy()

            for cmd_name in commands:
                try:
                    self.remove_command(cmd_name)
                except exceptions.YamiException:
                    raise exceptions.ModuleLoadException(
                        f"Error with unloading module {module} due to command '{cmd_name}'"
                    )

            removed = self._modules.pop(name)
            removed._loaded = False
            return removed

        raise ValueError(f"Failed to remove module '{name}', it was not found")

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

        name = name or command.__name__
        cmd = commands_.MessageCommand(command, name, description, aliases)
        return self.add_command(cmd)

    def remove_command(self, name: str) -> commands_.MessageCommand:
        if cmd := self._commands.pop(name):
            if mod := cmd.module:
                mod.remove_command(cmd.name)

            return cmd

        raise ValueError(f"Failed to remove command '{name}', it was not found")

    def yield_commands(self) -> typing.Generator[commands_.MessageCommand, None, None]:
        """Yields commands attached to the bot.

        Returns:
            Generator[yami.MessageCommand, ...]
        """
        yield from self._commands.values()

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
                name or callback.__name__,
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

        annots = tuple(inspect.signature(cmd.callback).parameters.values())
        ctx = context.MessageContext(self, event.message, cmd, p)
        converted: list[typing.Any] = []
        offset = 2 if cmd.module else 1

        for i, arg in enumerate(parsed):
            a = annots[i + offset].annotation
            t = getattr(builtins, a, str) if isinstance(a, str) else a

            if t is bool:
                if arg == "True":
                    converted.append(True)
                elif arg == "False":
                    converted.append(False)
                else:
                    raise exceptions.BadArgument(
                        f"Invalid arg '{arg}' for {bool} in '{cmd.name}' at position {i + offset}"
                    ) from None
                continue

            try:
                converted.append(t(arg)) if type(t) in (type, str) else converted.append(arg)
            except (TypeError, ValueError):
                raise exceptions.BadArgument(
                    f"Invalid arg '{arg}' for {t} in '{cmd.name}' at position {i + 1}"
                ) from None

        if m := cmd.module:
            await cmd.callback(m, ctx, *converted)
        else:
            await cmd.callback(ctx, *converted)
