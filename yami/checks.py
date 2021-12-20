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

import functools
from typing import Any, Callable

from yami import context, exceptions

__all__ = ["is_owner"]


def is_owner(cb: Callable[..., Any]) -> Callable[..., Any]:
    """MessageCommand decorator that registers a check to the command
    invocations. Must be placed below the command decorator.
    """

    @functools.wraps(cb)
    async def _check(ctx: context.MessageContext, *args: Any, **kwargs: Any) -> Any:
        if ctx.author.id not in ctx.bot.owner_ids:
            raise exceptions.CheckException(
                f"Command '{ctx.command.name}' failed - you are not the owner of this application."
            )
        return await cb(ctx, *args, **kwargs)

    return _check
