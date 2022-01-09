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
"""Yami exceptions."""

from __future__ import annotations

__all__ = [
    "YamiException",
    "CommandException",
    "CommandNotFound",
    "BadArgument",
    "DuplicateCommand",
    "ModuleException",
    "ModuleRemoveException",
    "ModuleAddException",
    "ModuleLoadException",
    "ModuleUnloadException",
    "CheckException",
    "BadCheck",
    "CheckRemovalFailed",
    "CheckFailed",
    "CheckAddFailed",
    "ListenerException",
    "TooManyArgs",
    "MissingArgs",
    "ConversionFailed",
]


class YamiException(Exception):
    """Base exception all Yami exceptions inherit from."""


class CommandException(YamiException):
    """Raised when an exception relating to a command occurs."""


class CommandNotFound(CommandException):
    """Raised when a command is invoked, or attempted to be accessed but
    no command with that name is found.
    """


class TooManyArgs(CommandException):
    """Raised when too many arguments are passed to a command."""


class MissingArgs(CommandException):
    """Raised when a command is run, but not all args are supplied."""


class BadArgument(CommandException):
    """Raised when a bad argument is passed to a message command."""


class ConversionFailed(YamiException):
    """Raised when the conversion performed by a converter fails."""


class DuplicateCommand(CommandException):
    """Raised when a command is added that shares a name or aliases with
    an existing command, or subcommand on the same level.
    """


class ModuleException(YamiException):
    """Raised when an error associated with a module occurs."""


class ModuleRemoveException(ModuleException):
    """Raised when a module fails to be removed from the bot."""


class ModuleUnloadException(ModuleException):
    """Raised when a module fails to be unloaded from the bot."""


class ModuleLoadException(ModuleException):
    """Raised when a module fails to be loaded to the bot."""


class ModuleAddException(ModuleException):
    """Raised when a module fails to be added to the bot."""


class CheckException(CommandException):
    """Raised when an exception relating to a check occurs."""


class BadCheck(CheckException):
    """Raised when a check decorator is placed below the command
    decorator, or otherwise used incorrectly.
    """


class CheckRemovalFailed(CheckException):
    """Raised when an invalid type is passed to remove_check."""


class CheckAddFailed(CheckException):
    """Raised when an invalid type is passed to add_check."""


class CheckFailed(CheckException):
    """Raised when a check is failed during command invocation."""


class ListenerException(YamiException):
    """Raised when an exception occurs relating to a module listener."""
