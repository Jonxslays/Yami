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

import importlib
import inspect
import os
import typing
from pathlib import Path

import hikari

from yami import args as args_
from yami import commands as commands_
from yami import context, exceptions
from yami import modules as modules_

__all__ = ["Bot"]


class Bot(hikari.GatewayBot):
    """A subclass of `hikari.GatewayBot` that provides an interface
    for handling commands.

    This is the class you will instantiate to utilize command features
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
        owner_ids: Sequence[int]
            A sequence of integers representing the Snowflakes of the
            bots owners. Defaults to an empty tuple.
        allow_extra_args: bool
            Whether or not the bot should allow extra args in command
            invocations. Defaults to `False`.
        **kwargs: The remaining kwargs for hikari.GatewayBot.
    """

    __slots__ = (
        "_prefix",
        "_case_insensitive",
        "_owner_ids",
        "_commands",
        "_aliases",
        "_modules",
        "_allow_extra_args",
    )

    def __init__(
        self,
        token: str,
        prefix: str | typing.Sequence[str],
        *,
        case_insensitive: bool = True,
        owner_ids: typing.Sequence[int] = (),
        allow_extra_args: bool = False,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(token, **kwargs)

        self._prefix: typing.Sequence[str] = (prefix,) if isinstance(prefix, str) else prefix
        self._aliases: dict[str, str] = {}
        self._case_insensitive = case_insensitive
        self._allow_extra_args = allow_extra_args
        self._commands: dict[str, commands_.MessageCommand] = {}
        self._modules: dict[str, modules_.Module] = {}
        self._owner_ids = tuple(owner_ids)

        self.subscribe(hikari.MessageCreateEvent, self._listen)
        self.subscribe(hikari.StartedEvent, self._setup_callback)

        for cmd in inspect.getmembers(self, lambda m: isinstance(m, commands_.MessageCommand)):
            cmd[1].was_globally_added = True
            self.add_command(cmd[1])

    @property
    def commands(self) -> dict[str, commands_.MessageCommand]:
        """A dictionary of name, MessageCommand pairs bound to the bot,
        including commands from any loaded modules.
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
        """A dictionary of name, `Module` pairs that are added to the
        bot, this includes unloaded modules.
        """
        return self._modules

    @property
    def owner_ids(self) -> typing.Sequence[int]:
        """A sequence of integers representing the Snowflakes of the
        bots owners.
        """
        return self._owner_ids

    @property
    def allow_extra_args(self) -> bool:
        """If `True` do not error when extra args are passed to a
        command. Defaults to `False`.
        """
        return self._allow_extra_args

    async def _setup_callback(self, _: hikari.StartedEvent) -> None:
        """Callback to guarantee the owner ids are known at runtime."""
        if not self._owner_ids:
            try:
                app = await self.rest.fetch_application()
            except hikari.HikariError:
                raise exceptions.YamiException(
                    "Application failed to setup - owner ids is unknown"
                )
            else:
                self._owner_ids = (app.owner.id,)

        self.unsubscribe(hikari.StartedEvent, self._setup_callback)

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

            for file in p.rglob("[!_]*.py") if recursive else p.glob("[!_]*.py"):
                self._load_all_modules(file, mod_state)

    def _load_all_modules(self, path: Path, mod_state: dict[str, modules_.Module]) -> None:
        """Load a given module onto the bot.

        Args:
            path: `Path`
                The path to load the modules from.
            mod_state: `dict[str, modules_.Module]`
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
            raise exceptions.ModuleLoadException(f"Failed to load module - {e}")

        for mod in filter(
            lambda m: inspect.isclass(m) and issubclass(m, modules_.Module),
            container.__dict__.values(),
        ):
            try:
                self._add_module(mod(self))
            except exceptions.ModuleAddException as e:
                self._modules = mod_state
                raise e
            else:
                mod.is_loaded = True

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
            raise exceptions.ModuleLoadException(f"Failed to import '{name}' - {e}")

        for mod in filter(
            lambda m: inspect.isclass(m) and issubclass(m, modules_.Module) and m.__name__ == name,
            container.__dict__.values(),
        ):
            mod = mod(self)

            try:
                if mod.is_loaded:
                    raise exceptions.ModuleLoadException(
                        f"Cannot load '{mod.name}' - it is already loaded"
                    )
                self._add_module(mod)

            except (exceptions.ModuleAddException, exceptions.ModuleLoadException) as e:
                self._modules = mod_state
                raise e

            mod.is_loaded = True

    def unload_module(self, name: str) -> modules_.Module:
        """Unloads a single module class with the given name. It will
        remain in `Bot.modules`, but just in an unloaded state and its
        commands will no longer be executable until it is loaded again.

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
            mod.is_loaded = False

            for cmd in mod.commands:
                try:
                    self.remove_command(cmd)
                except exceptions.CommandNotFound:
                    # We are unloading the module regardless
                    continue
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
            )

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
        raise_conversion: bool = False
    ) -> commands_.MessageCommand:
        """Adds a command to the bot.

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
            `yami.DuplicateCommand`
                If the command shares a name or alias with an existing
                command.
            `yami.BadArgument`
                If aliases is not a list or a tuple.
        """
        if isinstance(command, commands_.MessageCommand):
            if not isinstance(command.aliases, (list, tuple)):
                raise exceptions.BadArgument(
                    f"Aliases must be a iterable of strings, not: {type(command.aliases)}"
                )

            if command.name in self._commands:
                raise exceptions.DuplicateCommand(
                    f"Failed to add command '{command.name}' to bot - name already in use",
                )

            for a in command.aliases:
                if a in self._aliases:
                    raise exceptions.DuplicateCommand(
                        f"Failed to add command '{command.name}' to bot "
                        f"- alias '{a}' already in use",
                    )

            self._aliases.update(dict((a, command.name) for a in command.aliases))
            self._commands[command.name] = command
            return command

        cmd = commands_.MessageCommand(
            command,
            name or command.__name__,
            description,
            aliases=aliases,
            raise_conversion=raise_conversion,
        )
        return self.add_command(cmd)

    def remove_command(self, name: str) -> commands_.MessageCommand:
        """Removes a command from the bot, and its module if it has one.

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
            return cmd.module.remove_command(name) if cmd.module else cmd

    def yield_commands(self) -> typing.Generator[commands_.MessageCommand, None, None]:
        """Yields commands attached to the bot, including all commands
        bound to modules that are loaded.

        Returns:
            `Generator[yami.MessageCommand, ...]`
                A generator over the bots commands.
        """
        yield from self._commands.values()

    def yield_modules(self) -> typing.Generator[modules_.Module, None, None]:
        """Yields the modules attached to the bot. This will yield both
        loaded, and unloaded modules.

        Returns:
            `Generator[yami.MessageCommand, ...]`
                A generator over the bots modules.
        """
        yield from self._modules.values()

    def get_command(self, name: str) -> commands_.MessageCommand | None:
        """Gets a command.

        Args:
            name: `str`
                The name or alias of the command to get.

        Returns:
            `yami.MessageCommand` | `None`
                The command, or None if not found.
        """
        return self._commands.get(self._aliases.get(name, name))

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
        raise_conversion: bool = False,
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
            raise_conversion: bool
                Whether or not to raise an error when a type hint
                conversion for the command arguments fails.

        Returns:
            `Callable[..., yami.MessageCommand]`
                The callback, but transformed into a message command.
        """
        return lambda callback: self.add_command(
            commands_.MessageCommand(
                callback,
                name or callback.__name__,
                description,
                aliases=aliases,
                raise_conversion=raise_conversion,
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

        if not name:
            # Skip this for now - occurs when there is a space between
            # the prefix and the next word in the message content
            return None

        # TODO: Fire a CommandInvokeEvent here once we make it
        # TODO: This is a mess, add a helper class or module

        if name in self._aliases:
            cmd = self._commands[self._aliases[name]]
        elif name in self._commands:
            cmd = self._commands[name]
        else:
            raise exceptions.CommandNotFound(f"No command found with name '{name}'")

        annots = tuple(inspect.signature(cmd.callback).parameters.values())
        annots = annots[2:] if cmd.module or cmd.was_globally_added else annots[1:]
        ctx = context.MessageContext(self, event.message, cmd, p)

        len_annots = len(annots)
        len_parsed = len(parsed)

        if len_parsed > len_annots and not self._allow_extra_args:
            raise exceptions.TooManyArgs(
                f"Too many args for {ctx.command} - expected "
                f"{len_annots} but got {len_parsed}"
            )

        if len_annots > len_parsed:
            print(annots, parsed)
            raise exceptions.MissingArgs(
                f"Missing args for {cmd} - expected {len_annots} but got {len_parsed} - missing"
                f" {', '.join(f'({a})' for a in annots[len_parsed - len_annots :])}"
            )

        for param, value in zip(annots, parsed):
            print("converting", value, "to", param)
            a = args_.MessageArg(param, value)
            print(a)

            try:
                await a.convert(ctx)
            except exceptions.ConversionFailed:
                raise exceptions.BadArgument("A bad argument was passed")

        for check in cmd.yield_checks():
            await check.execute(ctx)

        vals = ctx.into_arg_values()

        print([*vals])

        if m := cmd.module:
            await cmd.callback(m, ctx, *ctx.into_arg_values())
        else:
            await cmd.callback(ctx, *ctx.into_arg_values())
