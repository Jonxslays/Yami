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
from dataclasses import dataclass

from yami import bot as bot_
from yami import commands as commands_

__all__ = ["Module"]


@dataclass
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

    def add_command(self, command: commands_.MessageCommand) -> None:
        """Adds a command to the module.

        Args:
            command: yami.MessageCommand
                The command to add.
        """
        if command.name in self._commands:
            raise ValueError(f"Failed to add command '{self.name}' - name already in use")

        self._commands[command.name] = command

    def remove_command(self, name: str) -> commands_.MessageCommand:
        """Removes a command from the module.

        Args:
            name: str
                The name of the command to remove. (case sensitive)
        """
        if name not in self.commands:
            raise ValueError(f"Failed to remove command '{self.name}' - it was not found")

        return self._commands.pop(name)

    def set_description(self, description: str) -> None:
        """Sets the modules description.

        Args:
            description: str
                The new description to set.
        """
        self._description = description
