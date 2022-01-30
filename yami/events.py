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
"""Module for Yami events."""

from __future__ import annotations

import abc

import hikari

from yami import bot as bot_
from yami import commands as commands_
from yami import context as context_

__all__ = ["YamiEvent", "CommandInvokeEvent", "CommandExceptionEvent"]


class YamiEvent(hikari.Event):
    """The base class all Yami events inherit from."""

    @property
    @abc.abstractmethod
    def app(self) -> bot_.Bot:
        ...


class CommandInvokeEvent(YamiEvent):
    """Fires when any command is invoked."""

    def __init__(self, ctx: context_.Context) -> None:
        self._ctx = ctx

    @property
    def app(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def ctx(self) -> context_.Context:
        """The context this event is attached to."""
        return self._ctx

    @property
    def command(self) -> commands_.MessageCommand:  # FIXME: make this generic
        """The command that triggered this event."""
        return self._ctx.command


class CommandExceptionEvent(YamiEvent):
    """Fires when a command encounters an exception of any kind."""

    def __init__(self, ctx: context_.Context, exc: Exception) -> None:
        self._ctx = ctx
        self._exc = exc

    @property
    def app(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def ctx(self) -> context_.Context:
        """The context this event is attached to."""
        return self._ctx

    @property
    def command(self) -> commands_.MessageCommand:  # FIXME: make this generic
        """The command that triggered this event."""
        return self._ctx.command

    @property
    def exception(self) -> Exception:
        """The exception that triggered this event."""
        return self._exc
