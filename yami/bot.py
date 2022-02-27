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
"""Module that contains the `yami.Bot` implementation."""

from __future__ import annotations

import importlib
import inspect
import logging
import os
import typing
from pathlib import Path

import hikari

from yami import args as args_
from yami import commands as commands_
from yami import context, events, exceptions
from yami import modules as modules_
from yami import utils

__all__ = ["Bot"]

_log = logging.getLogger(__name__)


class Bot(hikari.GatewayBot):
    """A subclass of :obj:`~hikari.impl.bot.GatewayBot` that provides an
    interface for handling commands.

    This is the class you will instantiate to utilize command features
    on top of the :obj:`~hikari.impl.bot.GatewayBot` superclass.

    .. warning::
        This class is slotted, if you want to set your own custom
        properties you have 2 choices:

        - Use the :obj:`Bot.shared` property which is an instance
          of :obj:`~yami.Shared`.

        - Subclass :obj:`Bot`, but this can lead to issues if you
          overwrite private or public attributes in your subclass.

    Args:
        token (:obj:`str`): The bot token to sign in with.

        prefix (:obj:`str` | :obj:`~typing.Sequence` [:obj:`str`]): The
            prefix, or sequence of prefixes to listen for. Planned
            support for mentions, and functions soon (tm).

    Keyword Args:
        owner_ids (:obj:`~typing.Sequence` [:obj:`int`]): A sequence
            of integers representing the Snowflakes of the bots owners.
            Defaults to ``()``.
        allow_extra_args (:obj:`bool`): Whether or not the bot should
            allow extra args in command invocations. Defaults to
            :obj:`False`.
        raise_cmd_not_found (:obj:`bool`): Whether or not to raise the
            :obj:`~yami.CommandNotFound` exception. Defaults to
            :obj:`False`.
        **kwargs (:obj:`~typing.Any`): The remaining kwargs for
            :obj:`~hikari.impl.bot.GatewayBot`.
    """

    __slots__ = (
        "_prefix",
        "_case_insensitive",
        "_owner_ids",
        "_commands",
        "_aliases",
        "_modules",
        "_allow_extra_args",
        "_shared",
        "_raise_cmd_not_found",
    )

    def __init__(
        self,
        token: str,
        prefix: str | typing.Sequence[str],
        *,
        owner_ids: typing.Sequence[int] = (),
        allow_extra_args: bool = False,
        raise_cmd_not_found: bool = False,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(token, **kwargs)

        self._prefix: typing.Sequence[str] = (prefix,) if isinstance(prefix, str) else prefix
        self._aliases: dict[str, str] = {}
        self._allow_extra_args = allow_extra_args
        self._raise_cmd_not_found = raise_cmd_not_found
        self._commands: dict[str, commands_.MessageCommand] = {}
        self._modules: dict[str, modules_.Module] = {}
        self._owner_ids = tuple(owner_ids)
        self._shared = utils.Shared()

        _log.debug(f"Initializing {self}")

        self.subscribe(hikari.MessageCreateEvent, self._listen)
        self.subscribe(hikari.StartedEvent, self._setup_callback)

        for cmd in inspect.getmembers(self, lambda m: isinstance(m, commands_.MessageCommand)):
            cmd[1].was_globally_added = True
            if not cmd[1].is_subcommand:
                self.add_command(cmd[1])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @property
    def commands(self) -> dict[str, commands_.MessageCommand]:
        """A dictionary of name, :obj:`~yami.MessageCommand` pairs bound
        to the bot, including commands from any loaded modules.
        """
        return self._commands

    @property
    def aliases(self) -> dict[str, str]:
        """A dictionary of aliases to their corresponding
        :obj:`~yami.MessageCommand` name.
        """
        return self._aliases

    @property
    def modules(self) -> dict[str, modules_.Module]:
        """A dictionary of name, :obj:`~yami.Module` pairs that are
        added to the bot, this includes unloaded modules.
        """
        return self._modules

    @property
    def owner_ids(self) -> typing.Sequence[int]:
        """A sequence of integers representing the ids of the bots
        owners.
        """
        return self._owner_ids

    @property
    def allow_extra_args(self) -> bool:
        """If :obj:`True` do not error when extra args are passed to a
        command.
        """
        return self._allow_extra_args

    @property
    def shared(self) -> utils.Shared:
        """The :obj:`~yami.Shared` instance associated with this bot."""
        return self._shared

    @property
    def raise_cmd_not_found(self) -> bool:
        """Returns :obj:`True` if this bot will raise a
        :obj:`~yami.CommandNotFound` exception when a prefix is used,
        but no command was found.
        """
        return self._raise_cmd_not_found

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
        _log.info(f"{self} is now ready to receive commands")

    def load_all_modules(self, *paths: str | Path, recursive: bool = True) -> None:
        """Loads all modules from each of the given paths.

        .. note::
            This method looks for all ``.py`` files that do not begin
            with an `_`. It is recursive by default.

            If this method fails partway through, the bots modules are
            reverted to their previous state and no modules will be
            loaded.

        Args:
            *paths (:obj:`str` | :obj:`~pathlib.Path`): One or more
                paths to load modules from.

        Keyword Args:
            recursive (:obj:`bool`): Whether or not to recurse into sub
                directories while loading modules.

        Raises:
            :obj:`~yami.ModuleLoadException`: When a module with the
                same name is already loaded on the bot, or when the
                named module is not found inside the given path's source
                file.
            :obj:`~yami.ModuleAddException`: When there is a failure
                with one of the commands in the module.
        """
        _log.debug(f"Loading all modules")
        mod_state = self._modules.copy()

        for p in paths:
            if not isinstance(p, Path):
                p = Path(os.path.relpath(p))

            for file in p.rglob("[!_]*.py") if recursive else p.glob("[!_]*.py"):
                self._load_all_modules(file, mod_state)

    def _load_all_modules(self, path: Path, mod_state: dict[str, modules_.Module]) -> None:
        """Load a given module onto the bot."""
        _log.debug(f"Importing all modules from {path}")

        if not (to_load := self._get_modules_from_container(path, mod_state)):
            return _log.debug("No modules found, continuing")

        for mod in to_load:
            _log.debug(f"Loading module {mod.__name__}()")
            self._try_load_module(mod, mod_state)

    def _get_modules_from_container(
        self, path: Path, mod_state: dict[str, modules_.Module], name: str | None = None
    ) -> list[typing.Type[modules_.Module]]:
        """Gets the Module objects from a given py file."""
        try:
            container = importlib.import_module(str(path).replace(".py", "").replace(os.sep, "."))
        except ModuleNotFoundError as e:
            self._modules = mod_state
            raise exceptions.ModuleLoadException(f"Failed to load module - {e}")

        return [
            *filter(
                lambda m: inspect.isclass(m)
                and issubclass(m, modules_.Module)
                and (m.__name__ == name if name else True),
                container.__dict__.values(),
            )
        ]

    def _try_load_module(
        self, mod: typing.Type[modules_.Module], mod_state: dict[str, modules_.Module]
    ) -> None:
        """Tries to load a Module."""
        try:
            instantiated = mod(self)
        except TypeError:
            self._modules = mod_state
            raise exceptions.ModuleLoadException(
                f"Failed to instantiate {mod.__name__}(), "
                "__init__ should only have one required arg - a yami.Bot instance"
            )

        try:
            if (
                old := [*filter(lambda m: m.name == instantiated.name, self._modules.values())]
            ) and old[0].is_loaded:
                self._modules = mod_state
                raise exceptions.ModuleLoadException(
                    f"Cannot load {instantiated} - it is already loaded"
                )
            self._add_module(instantiated)
        except exceptions.ModuleAddException as e:
            self._modules = mod_state
            raise e
        else:
            mod.is_loaded = True  # type: ignore
            _log.debug(f"Loaded module {instantiated}")

    def load_module(self, name: str, path: str | Path) -> None:
        """Loads a single module class from the path specified.

        .. note::

            If this method fails partway through, the bots modules are
            reverted to their previous state and the module will not be
            loaded.

        Args:
            name (:obj:`str`): The name of the module class to load.
                (case sensitive)
            path (:obj:`str` | :obj:`~pathlib.Path`): The path to load
                the module from.

        Raises:
            :obj:`~yami.ModuleLoadException`: When a module with the
                same name is already loaded on the bot, or when the
                named module is not found inside the given paths source
                file.
            :obj:`~yami.ModuleAddException`: When there is a failure
                with one of the commands in the module.
        """
        _log.debug(f"Loading module '{name}' from {path}")
        mod_state = self._modules.copy()

        if not isinstance(path, Path):
            path = Path(os.path.relpath(path))

        for mod in self._get_modules_from_container(path, mod_state, name):
            self._try_load_module(mod, mod_state)

    def unload_module(self, name: str) -> modules_.Module:
        """Unloads a single module class with the given name. It will
        remain in :obj:`Bot.modules`, but just in an unloaded state and
        its commands will no longer be executable until it is loaded
        again.

        Args:
            name (:obj:`str`): The name of the module class to unload.
                (case sensitive)

        Returns:
            :obj:`~yami.Module`: The module that was unloaded.

        Raises:
            :obj:`~yami.ModuleUnloadException`: When no module with this
                name was found.
        """
        _log.debug(f"Unloading module '{name}'")

        if mod := self._modules.get(name):
            mod.is_loaded = False

            for cmd in mod.commands:
                try:
                    self.remove_command(cmd)
                except exceptions.CommandNotFound:
                    # We are unloading the module regardless
                    _log.warning(f"Error removing {cmd} from {self}, continuing")
                    continue

            _log.debug(f"Unloaded module {mod}")
            return mod

        raise exceptions.ModuleUnloadException(
            f"Failed to unload module '{name}' from bot - it was not found"
        )

    def remove_module(self, name: str) -> modules_.Module:
        """Removes a single module class with the given name. It will
        no longer be accessible via :obj:`Bot.modules`.

        Args:
            name (:obj:`str`): The name of the module class to remove.
                (case sensitive)

        Returns:
            :obj:`~yami.Module`: The module that was removed.

        Raises:
            :obj:`~yami.ModuleRemoveException`: When no module with this
                name was found.
        """
        _log.debug(f"Removing module '{name}'")

        try:
            self.unload_module(name)
        except exceptions.ModuleUnloadException:
            raise exceptions.ModuleRemoveException(
                f"Failed to remove module '{name}' from bot - it was not found"
            )

        mod = self._modules.pop(name)
        _log.debug(f"Removed module {mod}")
        return mod

    def _add_module(self, module: modules_.Module) -> None:
        """Adds a `yami.Module` to the bot."""
        if module.name in self._modules and module.is_loaded:
            raise exceptions.ModuleAddException(
                f"Failed to add module {module} to bot - it is already added and loaded"
            )

        cmd_state = self._commands.copy()
        for cmd in module.commands.values():
            try:
                self.add_command(cmd)
            except exceptions.YamiException:
                self._commands = cmd_state
                raise exceptions.ModuleAddException(f"Failed to add {module} to bot due to {cmd}")

        self._modules[module.name] = module

    def add_command(
        self,
        command: typing.Callable[..., typing.Any] | commands_.MessageCommand,
        *,
        name: str | None = None,
        description: str = "",
        aliases: list[str] | tuple[str, ...] = [],
        raise_conversion: bool = False,
    ) -> commands_.MessageCommand:
        """Adds a command to the bot.

        Args:
            command (:obj:`~typing.Callable` [..., :obj:`~typing.Any`] \
                | :obj:`~yami.MessageCommand`): The command or callback
                to add.

        Keyword Args:
            name (:obj:`str` | :obj:`None`): The name of the command.
                Defaults to the function name.
            description (:obj:`str`): The commands description. Defaults
                to ``""``.
            aliases (:obj:`~typing.Iterable` [:obj:`str`]): The commands
                aliases. Defaults to ``[]``.
            raise_conversion(:obj:`bool`): Whether or not to raise an
                exception if argument conversion fails. Defaults to
                :obj:`False`.

        Returns:
            :obj:`~yami.MessageCommand`: The command that was added.

        Raises:
            :obj:`~yami.DuplicateCommand`: If the command shares a name
                or alias with an existing command.
            :obj:`TypeError`: If aliases is not a list or a tuple.
        """
        if isinstance(command, commands_.MessageCommand):
            if not command.module:
                _log.debug(f"Adding {command} to {self}")

            if not isinstance(command.aliases, (list, tuple)):
                raise TypeError(
                    f"Aliases must be a iterable of strings, not: {type(command.aliases)}"
                )

            if command.name in self._commands:
                raise exceptions.DuplicateCommand(
                    f"Failed to add command {command} to bot - name already in use"
                )

            for alias in filter(lambda a: a in self._aliases, command.aliases):
                raise exceptions.DuplicateCommand(
                    f"Failed to add command {command} to bot " f"- alias {alias!r} already in use"
                )

            self._aliases.update({a: command.name for a in command.aliases})
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
        """Removes a :obj:`~yami.MessageCommand` from the :obj:`Bot`,
        and its :obj:`yami.Module` if it has one.

        Args:
            name (:obj:`str`): The name of the command to remove.

        Returns:
            :obj:`~yami.MessageCommand`: The command that was removed.

        Raises:
            :obj:`~yami.CommandNotFound`: When the command was not
                found.
        """
        try:
            cmd = self._commands.pop(name)
        except KeyError:
            raise exceptions.CommandNotFound(
                f"Failed to remove command '{name}' from bot - it was not found"
            ) from None
        else:
            if cmd.module and cmd.module.is_loaded:
                return cmd.module.remove_command(name)

        _log.debug(f"Removed {cmd} from {self}")
        return cmd

    def iter_commands(self) -> typing.Generator[commands_.MessageCommand, None, None]:
        """Iterates the bots commands.

        Returns:
            :obj:`~typing.Generator`: A generator over the commands.

        Yields:
            :obj:`~yami.MessageCommand`: Each command.
        """
        yield from self._commands.values()

    def iter_modules(self) -> typing.Generator[modules_.Module, None, None]:
        """Iterates over the modules attached to the bot. This will
        included both loaded and unloaded modules.

        Returns:
            :obj:`~typing.Generator`: A generator over the modules.

        Yields:
            :obj:`~yami.Module`: Each module.
        """
        yield from self._modules.values()

    def iter_loaded_modules(self) -> typing.Generator[modules_.Module, None, None]:
        """Iterates over the modules attached to the bot. This will
        only include loaded modules.

        Returns:
            :obj:`~typing.Generator`: A generator over the modules.

        Yields:
            :obj:`~yami.Module`: Each loaded module.
        """
        yield from (m for m in self._modules.values() if m.is_loaded)

    def get_command(self, name: str) -> commands_.MessageCommand | None:
        """Gets a command.

        Args:
            name (:obj:`str`): The name or alias of the command to get.

        Returns:
            :obj:`~yami.MessageCommand` | :obj:`None`:
                The command, or :obj:`None` if not found.
        """
        return self._commands.get(self._aliases.get(name, name))

    def get_module(self, name: str) -> modules_.Module | None:
        """Gets a module.

        Args:
            name (:obj:`str`): The name of the module to get.

        Returns:
            :obj:`yami.Module` | :obj:`None`:
                The module, or :obj:`None` if not found.
        """
        return self._modules.get(name)

    def command(
        self,
        name: str | None = None,
        description: str = "",
        *,
        aliases: typing.Sequence[str] = (),
        raise_conversion: bool = False,
        invoke_with: bool = False,
    ) -> typing.Callable[..., typing.Any]:
        """Decorator to add a :obj:`~yami.MessageCommand` to the bot.
        This should be placed immediately above the command callback.
        Any checks should be placed above this decorator.

        Args:
            name (:obj:`str`): The name of the command. Defaults to the
                function name.
            description (:obj:`str`): The command description. If
                omitted, the callbacks docstring will be used instead.

        Keyword Args:
            aliases (:obj:`~typing.Sequence` [:obj:`str`]): A list or
                tuple of aliases for the command.
            raise_conversion (:obj:`bool`): Whether or not to raise an
                exception when a type hint conversion for the command
                arguments fails.

        Returns:
            :obj:`~typing.Callable` [..., :obj:`~yami.MessageCommand`]:
                A message command crafted from the callback, and
                decorator arguments.
        """
        return lambda callback: self.add_command(
            commands_.MessageCommand(
                callback,
                name or callback.__name__,
                description or callback.__doc__ or "",
                aliases=aliases,
                raise_conversion=raise_conversion,
                invoke_with=invoke_with,
            )
        )

    async def _listen(self, e: hikari.MessageCreateEvent) -> None:
        """Listens for messages and invokes if they begin with one of
        the bots prefixes.
        """
        if not e.message.content:
            return

        for p in self._prefix:
            if e.message.content.startswith(p):
                return await self._invoke(p, e, e.message.content)

    def _parse_for_subcommands(
        self,
        cmd: commands_.MessageCommand,
        parsed: list[str],
        subcommands: list[commands_.MessageCommand] = [],
    ) -> list[commands_.MessageCommand]:
        """Recursively parses for subcommands."""
        if parsed and parsed[0] in cmd.subcommands:
            sub = cmd.subcommands[parsed.pop(0)]
            subcommands.append(sub)
            subcommands = self._parse_for_subcommands(sub, parsed, subcommands)

        return subcommands

    async def _invoke(self, p: str, event: hikari.MessageCreateEvent, content: str) -> None:
        """Attempts to invoke a command."""

        # Get the prefix and the name of the command
        parsed = content.split()
        name = parsed.pop(0)[len(p) :]
        if name == "":
            # If there is whitespace between the prefix and the command.
            name = parsed.pop(0)

        if name in self._aliases:
            cmd = self._commands[self._aliases[name]]
        elif name in self._commands:
            cmd = self._commands[name]
        elif self._raise_cmd_not_found:
            raise exceptions.CommandNotFound(f"No command found with name {name!r}")
        else:
            return None

        ctx = context.MessageContext(self, event.message, cmd, p)
        await self.dispatch(events.CommandInvokeEvent(ctx))

        try:
            all_invoked = (cmd, *self._parse_for_subcommands(cmd, parsed))

            for i, c in enumerate(all_invoked):
                is_final = i + 1 >= len(all_invoked)
                for check in c.iter_checks():
                    await check.execute(ctx)

                if c.is_subcommand:
                    if c.invoke_with or is_final:
                        ctx._invoked_subcommands.append(c)
                    else:
                        continue

                for arg in self._get_args(c, parsed):
                    await arg.convert(ctx)

                await self._invoke_callback(ctx, c)

                if not is_final:
                    ctx.args.clear()

        except Exception as e:
            ctx.exceptions.append(e)
            await self.dispatch(events.CommandExceptionEvent(ctx))

        else:
            await self.dispatch(events.CommandSuccessEvent(ctx))

    def _get_args(
        self,
        cmd: commands_.MessageCommand,
        parsed: list[str],
    ) -> list[args_.MessageArg]:
        """Parses for args."""
        annots = tuple(inspect.signature(cmd.callback).parameters.values())
        annots = annots[2:] if cmd.module or cmd.was_globally_added else annots[1:]
        annots_l = len(annots)
        parsed_l = len(parsed)

        args: list[args_.MessageArg] = []
        args.extend(args_.MessageArg(a, p) for a, p in zip(annots, parsed))

        if parsed_l > annots_l:
            if not self._allow_extra_args:
                raise exceptions.TooManyArgs(
                    f"{cmd} received too many args - expected {annots_l} but got {parsed_l}"
                )

        if parsed_l < annots_l:
            raise exceptions.MissingArgs(
                f"{cmd} is missing a required argument - expected {annots_l} but got {parsed_l}"
            )

        return args

    async def _execute_checks(
        self, ctx: context.MessageContext, cmd: commands_.MessageCommand
    ) -> None:
        """Executes the given commands checks."""
        for check in cmd.iter_checks():
            await check.execute(ctx)

    async def _invoke_callback(
        self, ctx: context.MessageContext, cmd: commands_.MessageCommand
    ) -> None:
        """Invokes the given commands callback."""
        if m := cmd.module:
            await cmd.callback(m, ctx, *ctx.iter_arg_values())
        elif cmd.was_globally_added:
            await cmd.callback(self, ctx, *ctx.iter_arg_values())
        else:
            await cmd.callback(ctx, *ctx.iter_arg_values())
