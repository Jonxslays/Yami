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
import logging
from typing import Any, Callable, Coroutine, Generator

import hikari

from yami import bot as bot_
from yami import commands as commands_
from yami import exceptions

__all__ = ["Module"]

_log = logging.getLogger(__name__)


class Module:
    """A collection of commands and functions that typically share a
    need for the same data, or are related in some way.

    - You should subclass `Module` to create your own modules.
    - Modules do not require any special functions in their file.

    If you overwrite the `__init__` method, it should take at least 1
    argument which is of type `yami.Bot`. Be sure to call
    `super().__init__(bot)` first thing.

    Yami takes care of importing the `Module` for you via the
    `Bot.load_module()` and `Bot.load_all_modules()` methods.
    """

    def __init__(self, bot: bot_.Bot) -> None:
        self._bot = bot
        self._is_loaded = False
        self._name = self.__class__.__name__
        self._description = self.__doc__ or ""
        self._commands: dict[str, commands_.MessageCommand] = {}
        self._listeners: dict[hikari.Event, Callable[..., Coroutine[Any, Any, None]]] = {}

        for cmd in inspect.getmembers(self, lambda m: isinstance(m, commands_.MessageCommand)):
            cmd[1]._module = self
            self.add_command(cmd[1])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    @property
    def name(self) -> str:
        """The name of this module."""
        return self._name

    @property
    def bot(self) -> bot_.Bot:
        """The bot this module belongs to."""
        return self._bot

    @property
    def commands(self) -> dict[str, commands_.MessageCommand]:
        """A dictionary of name, MessageCommand pairs this module
        has.
        """
        return self._commands

    @property
    def description(self) -> str:
        """The description of this module."""
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        self._description = description

    @property
    def is_loaded(self) -> bool:
        """Whether or not this module is currently loaded."""
        return self._is_loaded

    @is_loaded.setter
    def is_loaded(self, value: bool) -> None:
        self._is_loaded = value

    def yield_commands(self) -> Generator[commands_.MessageCommand, None, None]:
        """Yields commands attached to the module.

        Returns:
            `Generator[yami.MessageCommand, ...]`
                A generator over the modules's commands.
        """
        yield from self._commands.values()

    def add_command(self, command: commands_.MessageCommand) -> None:
        """Adds a command to the module.

        Args:
            command: `yami.MessageCommand`
                The command to add.

        Raises:
            `yami.DuplicateCommand`
                When a command with this name already exists.
        """
        _log.debug(f"Adding {command} to {self}")

        if command.name in self._commands:
            raise exceptions.DuplicateCommand(
                f"Failed to add command to '{self._name}' - name '{command.name}' already in use"
            )

        if self._is_loaded:
            self._bot.add_command(command)

        self._commands[command.name] = command

    def remove_command(self, name: str) -> commands_.MessageCommand:
        """Removes a command from the module.

        Args:
            name: `str`
                The name of the command to remove. (case sensitive)

        Raises:
            yami.CommandNotFound:
                When a command with this name is not found.
        """
        if name not in self.commands:
            raise exceptions.CommandNotFound(
                f"Failed to remove command from '{self}' - name '{name}' not found"
            )

        if self._is_loaded and name in self._bot.commands:
            self._bot.remove_command(name)

        cmd = self._commands.pop(name)
        _log.debug(f"Removed {cmd} from {self}")
        return cmd
