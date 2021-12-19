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

__all__ = [
    "YamiException",
    "CommandNotFound",
    "AsyncRequired",
    "BadArgument",
    "DuplicateCommand",
    "ModuleException",
    "ModuleAlreadyDetached",
    "ModuleLoadException",
]


class YamiException(Exception):
    """Base exception all Yami exceptions inherit from."""


class CommandException(YamiException):
    """Raised when an execption relating to a command occurs."""


class CommandNotFound(CommandException):
    """Raised when a command is invoked with a valid prefix, but no
    command with that name is found.
    """


class AsyncRequired(CommandException):
    """Raised when a synchronous command is added to the bot via the
    yami.legacy decorator.
    """


class BadArgument(CommandException):
    """Raised what a bad argument is passed to a message command."""


class DuplicateCommand(CommandException):
    """Raised when a command is added that shares a name or aliases with
    an existing command.
    """


class ModuleException(YamiException):
    """Raised when an error associated with a module occurs."""


class ModuleAlreadyDetached(ModuleException):
    """Raised when an attempt is made to detach a module, but the module
    is not attached to any bot.
    """


class ModuleLoadException(ModuleException):
    """Raised when a module fails to load usually due to some command
    issue.
    """
