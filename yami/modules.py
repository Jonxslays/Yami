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
from dataclasses import dataclass

from yami import bot as bot_
from yami import commands as commands_
from yami import exceptions

__all__ = ["Module"]


@dataclass
class Module:
    """A collection of commands and functions that (typically) share
    a need for the same data, or are related in some way.

    You should subclass `Module` to create your own modules.
    """

    def __init__(self) -> None:
        self._bot: bot_.Bot | None = None
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
    def commands(self) -> dict[str, commands_.MessageCommand]:
        return self._commands

    @property
    def description(self) -> str:
        """The description of this module."""
        return self._description

    @property
    def is_loaded(self) -> bool:
        """Whether or not this module is currently loaded."""
        return self._bot is not None

    @classmethod
    def attach(cls, bot: bot_.Bot) -> None:
        """Attaches the module to the given bot.

        Args:
            bot: yami.Bot
                The bot to sync with.
        """
        m = cls()
        m._bot = bot
        bot.sync_module(m)

    @classmethod
    def command(
        cls,
        name: str | None = None,
        description: str = "",
        *,
        aliases: typing.Iterable[str] = [],
    ) -> typing.Callable[..., commands_.MessageCommand]:
        """Decorator to add commands to the bot inside of modules."""
        return lambda callback: commands_.MessageCommand(
            callback,
            name or callback.__name__,
            description,
            aliases,
        )

    def add_command(self, command: commands_.MessageCommand) -> None:
        if command.name in self._commands:
            raise ValueError(f"Failed to add command '{self.name}' - name already in use")

        self._commands[command.name] = command

    def remove_command(self, name: str) -> commands_.MessageCommand:
        if name not in self.commands:
            raise ValueError(f"Failed to remove command '{self.name}' - it was not found")

        return self._commands.pop(name)

    def detach(self) -> None:
        """Detaches the module from the given bot."""
        if self._bot:
            self._bot.desync_module(self._name)
            self._bot = None
            return None

        raise exceptions.ModuleAlreadyDetached(
            f"Failed to detach module '{self.name}', it is already detached"
        )

    def set_description(self, description: str) -> None:
        """Sets the modules description.

        Args:
            description: str
                The new description to set.
        """
        self._description = description
