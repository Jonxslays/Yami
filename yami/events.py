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
from yami import commands, context

__all__ = ["YamiEvent", "CommandInvokeEvent", "CommandExceptionEvent", "CommandSuccessEvent"]


class YamiEvent(hikari.Event, abc.ABC):
    """The base class all Yami events inherit from."""

    @property
    @abc.abstractmethod
    def app(self) -> bot_.Bot:
        ...

    @property
    @abc.abstractmethod
    def bot(self) -> bot_.Bot:
        ...


class CommandInvokeEvent(YamiEvent):
    """Fires when any command is invoked."""

    def __init__(self, ctx: context.Context) -> None:
        self._ctx = ctx

    @property
    def app(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def bot(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def ctx(self) -> context.Context:
        """The context this event is attached to."""
        return self._ctx

    @property
    def command(self) -> commands.MessageCommand:  # FIXME: make this generic
        """The command that triggered this event."""
        return self._ctx.command


class CommandSuccessEvent(YamiEvent):
    """Fires when any command invocation is successful."""

    def __init__(self, ctx: context.Context) -> None:
        self._ctx = ctx

    @property
    def app(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def bot(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def ctx(self) -> context.Context:
        """The context this event is attached to."""
        return self._ctx

    @property
    def command(self) -> commands.MessageCommand:  # FIXME: make this generic
        """The command that triggered this event."""
        return self._ctx.command


class CommandExceptionEvent(YamiEvent):
    """Fires when a command encounters an exception of any kind."""

    def __init__(self, ctx: context.Context) -> None:
        self._ctx = ctx

    @property
    def app(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def bot(self) -> bot_.Bot:
        """The app (Bot) associated with this event."""
        return self._ctx.bot

    @property
    def ctx(self) -> context.Context:
        """The context this event is attached to."""
        return self._ctx

    @property
    def command(self) -> commands.MessageCommand:  # FIXME: make this generic
        """The command that triggered this event."""
        return self._ctx.command

    @property
    def exceptions(self) -> list[Exception]:
        """The exception that triggered this event."""
        return self._ctx.exceptions
