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

import abc

from yami import commands, context, exceptions

__all__ = ["is_owner", "Check", "is_in_guild"]


class Check(abc.ABC):
    """Base class all Yami checks inherit from."""

    __slots__ = ()

    def __init__(self, obj: commands.MessageCommand | None = None) -> None:
        if obj is not None:
            self._bind(obj)

    def __call__(self, obj: commands.MessageCommand | None = None) -> None:
        if obj is not None:
            self._bind(obj)

    def _bind(self, obj: commands.MessageCommand) -> None:
        try:
            obj.add_check(self)
        except AttributeError:
            raise exceptions.BadCheckPlacement(
                f"'{obj.__name__}' is not a MessageCommand - "  # type: ignore
                "move this decorator above the command decorator"
            ) from None

    def _raise(self, ctx: context.MessageContext, msg: str) -> None:
        """Raised a CheckFailed exception for a command name and with
        the given message
        """
        e = exceptions.CheckFailed(f"Command '{ctx.command.name}' failed - {msg}")
        ctx.exceptions.append(e)
        raise e

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abc.abstractmethod
    def execute(self, ctx: context.MessageContext) -> None:
        """Executes the check.

        Args:
            ctx: yami.MessageContext
                The context to execute the check against.

        Raises:
            `yami.CheckFailed`
                When the check fails.
        """


class is_owner(Check):
    """Fails if the author of the command is not the bots owner.

    Who is the bots owner:
    - Any user with an id matching one of the ids passed into the bots
    constructor for the kwarg `owner_ids`.
    - The application owner fetched from discord if no `owner_ids` were
    passed to the constructor.
    """

    __slots__ = ()

    def execute(self, ctx: context.MessageContext) -> None:
        if ctx.author.id not in ctx.bot.owner_ids:
            self._raise(ctx, "you are not the owner of this application")


class is_in_guild(Check):
    """Fails if the command was not run in a guild."""

    __slots__ = ()

    def execute(self, ctx: context.MessageContext) -> None:
        if not ctx.guild_id:
            self._raise(ctx, "this command can only be run in a guild")
