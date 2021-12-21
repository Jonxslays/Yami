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
from typing import Any, Callable, Coroutine, Generator

import hikari

from yami import bot as bot_
from yami import commands as commands_
from yami import exceptions

__all__ = ["Module"]


class Module:
    """A collection of commands and functions that typically share a
    need for the same data, or are related in some way.

    You should subclass `Module` to create your own modules.
    """

    def __init__(self, bot: bot_.Bot) -> None:
        self._bot = bot
        self._loaded = False
        self._name = self.__class__.__name__
        self._description = self.__doc__ or ""
        self._commands: dict[str, commands_.MessageCommand] = {}
        self._listeners: dict[hikari.Event, Callable[..., Coroutine[Any, Any, None]]] = {}

        for cmd in inspect.getmembers(self, lambda m: isinstance(m, commands_.MessageCommand)):
            cmd[1]._module = self
            self.add_command(cmd[1])

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

    @property
    def is_loaded(self) -> bool:
        """Whether or not this module is currently loaded."""
        return self._loaded

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
        if command.name in self._commands:
            raise exceptions.DuplicateCommand(
                f"Failed to add command to '{self._name}' - name '{command.name}' already in use"
            )

        if self._loaded:
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
                f"Failed to remove command from '{self._name}' - name '{name}' not found"
            )

        if self._loaded:
            if name in self._bot.commands:
                self._bot.remove_command(name)

        return self._commands.pop(name)

    def set_description(self, description: str) -> None:
        """Sets the modules description.

        Args:
            description: `str`
                The new description to set.
        """
        self._description = description
