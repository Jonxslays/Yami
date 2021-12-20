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
        owner_ids: typing.Sequence[int] = (),
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(token, **kwargs)

        self._prefix: typing.Sequence[str] = (prefix,) if isinstance(prefix, str) else prefix
        self._aliases: dict[str, str] = {}
        self._case_insensitive = case_insensitive
        self._commands: dict[str, commands_.MessageCommand] = {}
        self._modules: dict[str, modules_.Module] = {}
        self._owner_ids = tuple(owner_ids)

        self.subscribe(hikari.MessageCreateEvent, self._listen)
        self.subscribe(hikari.StartedEvent, self._setup_callback)

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

    @property
    def owner_ids(self) -> typing.Sequence[int]:
        return self._owner_ids

    async def _setup_callback(self, event: hikari.StartedEvent) -> None:
        """Callback to guarantee the owner ids are known at runtime."""
        if not self._owner_ids:
            app = await self.rest.fetch_application()
            self._owner_ids = (app.owner.id,)

        self.unsubscribe(hikari.StartedEvent, self._setup_callback)

    def get_alias_command(self, alias: str) -> commands_.MessageCommand | None:
        """Helper method to get the command associated with an alias.

        Args:
            alias: `str`
                The alias to get the command for.

        Returns:
            `yami.MessageCommand` | `None`
                The command, or None if not found.
        """
        return self._commands.get(self.aliases.get(alias, alias))

    def load_all_modules(self, *paths: str | Path, recursive: bool = True) -> None:
        """Loads all modules from each of the given paths.This method
        looks for all `.py` files that do not begin with an `_`. It is
        recursive by default.

        If this method fails partway through, the bots module's are
        reverted to their state from before this method was called and
        no modules will be added.

        Args:
            *paths: `str` | `pathlib.Path`
                One or multiple paths to load modules from.

        Raises:
            `yami.ModuleAddException`
                When a module with the same name is already added to the
                bot, or there is a failure with one of the commands in
                the module.
        """
        mod_state = self._modules.copy()

        for p in paths:
            if not isinstance(p, Path):
                p = Path(os.path.relpath(p))

            mod_filter = (
                filter(
                    lambda m: not m.stem.startswith("_"),
                    (p.rglob("*.py") if recursive else p.glob("*.py")),
                )
                if p.is_dir()
                else (p,)
            )

            for file in mod_filter:
                self._load_all_modules(file, mod_state)

    def _load_all_modules(self, path: Path, mod_state: dict[str, modules_.Module]) -> None:
        """Load a given module onto the bot.

        Args:
            path: Path
                The path to load the modules from.
            mod_state: dict[str, modules_.Module]
                The state to revert to if there is an error while
                loading this module.

        Raises:
            `yami.ModuleAddException`
                When a module with the same name is already added to the
                bot, or there is a failure with one of the commands in
                the module.
        """
        try:
            container = importlib.import_module(str(path).replace(".py", "").replace(os.sep, "."))
        except ModuleNotFoundError as e:
            self._modules = mod_state
            raise exceptions.ModuleLoadException(f"Failed to load module - {e}") from None

        for mod in filter(
            lambda m: inspect.isclass(m) and issubclass(m, modules_.Module),
            container.__dict__.values(),
        ):
            try:
                self._add_module(mod(self))
            except exceptions.ModuleAddException as e:
                self._modules = mod_state
                raise e from None
            else:
                mod._loaded = True

    def load_module(self, name: str, path: str | Path) -> None:
        """Loads a single module class from the path specified.

        If this method fails partway through, the bots module's are
        reverted to their state from before this method was called and
        no modules will be added.

        Args:
            name: `str`
                The name of the module class to load. (case sensitive)
            path: `str` | `pathlib.Path`
                The path to load the module from.

        Raises:
            `yami.ModuleLoadException`
                When a module with the same name is already loaded on
                the bot, or when the named module is not found inside
                the given path's source file.
            `yami.ModuleAddException`
                When there is a failure with one of the commands in
                the module.
        """
        mod_state = self._modules.copy()

        if not isinstance(path, Path):
            path = Path(os.path.relpath(path))

        try:
            container = importlib.import_module(str(path).replace(".py", "").replace(os.sep, "."))
        except ModuleNotFoundError as e:
            self._modules = mod_state
            raise exceptions.ModuleLoadException(f"Failed to import '{name}' - {e}") from None

        for mod in filter(
            lambda m: inspect.isclass(m) and issubclass(m, modules_.Module) and m.__name__ == name,
            container.__dict__.values(),
        ):
            try:
                if mod.is_loaded:
                    raise exceptions.ModuleLoadException(
                        f"Cannot load '{mod.name}' - it is already loaded"
                    )
                self._add_module(mod(self))

            except (exceptions.ModuleAddException, exceptions.ModuleLoadException) as e:
                self._modules = mod_state
                raise e from None

            mod._loaded = True

    def unload_module(self, name: str) -> modules_.Module:
        """Unloads a single module class with the given name. It will
        remain in `Bot.modules`, but just in an unloaded state.

        Args:
            name: `str`
                The name of the module class to unload. (case sensitive)

        Returns:
            `yami.Module`
                The module that was unloaded.

        Raises:
            `yami.ModuleUnloadException`
                When no module with this name was found.
        """
        if mod := self._modules.get(name):
            for cmd in mod.commands:
                try:
                    self.remove_command(cmd)
                except exceptions.CommandNotFound:
                    # We are unloading the module regardless
                    continue

            mod._loaded = False
            return mod

        raise exceptions.ModuleUnloadException(
            f"Failed to unload module '{name}' from bot - it was not found"
        )

    def remove_module(self, name: str) -> modules_.Module:
        """Removes a single module class with the given name. It will
        no longer be accessible via `Bot.modules`.

        Args:
            name: `str`
                The name of the module class to remove. (case sensitive)

        Returns:
            `yami.Module`
                The module that was removed.

        Raises:
            `yami.ModuleRemoveException`
                When no module with this name was found.
        """
        try:
            self.unload_module(name)
        except exceptions.ModuleUnloadException:
            raise exceptions.ModuleRemoveException(
                f"Failed to remove module '{name}' from bot - it was not found"
            ) from None

        return self._modules.pop(name)

    def _add_module(self, module: modules_.Module) -> None:
        """Adds a `yami.Module` to the bot.

        Args:
            module: `yami.Module`
                The module to add to the bot.

        Raises:
            `yami.ModuleAddException`
                When a module with the same name is already added to the
                bot and loaded, or there is a failure with one of the
                commands in the module.
        """
        if module.name in self._modules and module.is_loaded:
            raise exceptions.ModuleAddException(
                f"Failed to add module'{module.name}' to bot - it is already added and loaded"
            )

        cmd_state = self._commands.copy()
        for cmd in module.commands.values():
            try:
                self.add_command(cmd)
            except exceptions.YamiException:
                self._commands = cmd_state
                raise exceptions.ModuleAddException(
                    f"Failed to add {module} to bot due to command '{cmd.name}'"
                )

        self._modules[module.name] = module

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

            if command.name in self._commands or any(a in self._aliases for a in command.aliases):
                raise exceptions.DuplicateCommand(
                    f"Failed to add command '{command.name}' to bot - name/alias already in use",
                )

            self._aliases.update(dict((a, command.name) for a in command.aliases))
            self._commands[command.name] = command
            return command

        name = name or command.__name__
        cmd = commands_.MessageCommand(command, name, description, aliases)
        return self.add_command(cmd)

    def remove_command(self, name: str) -> commands_.MessageCommand:
        """Removes a command from the bot.

        Args:
            command: `Callable[..., Any]` | `yami.MessageCommand`
                The command to add.

        Kwargs:
            name: `str` | `None`
                The name of the command (defaults to the function name)
            description: `str`
                The command descriptions (defaults to "")
            aliases: `Iterable[str]`
                The command aliases (defaults to [])

        Returns:
            `yami.MessageCommand`
                The command that was added.

        Raises:
            `yami.CommandNotFound`
                If the command was not found.
        """
        try:
            cmd = self._commands.pop(name)
        except KeyError:
            raise exceptions.CommandNotFound(
                f"Failed to remove command '{name}' from bot - it was not found"
            ) from None
        else:
            return cmd

    def yield_commands(self) -> typing.Generator[commands_.MessageCommand, None, None]:
        """Yields commands attached to the bot.

        Returns:
            `Generator[yami.MessageCommand, ...]`
                A generator over the bot's commands.
        """
        yield from self._commands.values()

    def yield_modules(self) -> typing.Generator[modules_.Module, None, None]:
        """Yields the modules attached to the bot. This will yield both
        loaded, and unloaded modules.

        Returns:
            `Generator[yami.MessageCommand, ...]`
                A generator over the bot's commands.
        """
        yield from self._modules.values()

    def get_command(self, name: str, *, alias: bool = False) -> commands_.MessageCommand | None:
        """Gets a command.

        Args:
            name: `str`
                The name of the command to get.

        Kwargs:
            alias: `bool`
                Whether or not to search aliases as well as names.
                Defaults to False.

        Returns:
            `yami.MessageCommand | None`
                The command, or None if not found.
        """
        if alias:
            name = self._aliases.get(name, name)

        return self._commands.get(name)

    def get_module(self, name: str) -> modules_.Module | None:
        """Gets a module.

        Args:
            name: `str`
                The name of the module to get.

        Returns:
           `yami.Module` | `None`
                The module, or None if not found.
        """
        return self._modules.get(name)

    def command(
        self,
        name: str | None = None,
        description: str = "",
        *,
        aliases: typing.Iterable[str] = [],
    ) -> typing.Callable[..., typing.Any]:
        """Decorator to add a message command to the bot.

        Args:
            name: `str`
                The name of the command. Defaults to the function name.
            description: `str`
                The command description. If omitted, the callbacks
                docstring will be used instead. REMINDER: docstrings are
                stripped from your programs bytecode when it is run with
                the `-OO` optimization flag.

        Kwargs:
            aliases: `Iterable[str]`
                A list or tuple of aliases for the command.

        Returns:
            `Callable[..., yami.MessageCommand]`
                The callback, but transformed into a message command.
        """
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
        # TODO: This is a mess, add a helper class or module

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
            if a is inspect.Signature.empty:
                converted.append(arg)
                continue

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
