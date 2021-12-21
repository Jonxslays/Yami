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
import inspect
from typing import Any, Callable, Sequence, cast

import hikari

from yami import commands, context, exceptions

__all__ = [
    "is_owner",
    "Check",
    "is_in_guild",
    "is_in_dm",
    "has_role",
    "has_any_role",
    "has_perms",
    "custom_check",
    "is_the_cutest",
]


class Check(abc.ABC):
    """Base class all Yami checks inherit from."""

    __slots__ = ("_obj",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if args or kwargs:
            print(args, kwargs)
            raise exceptions.BadCheck(
                f"Unclosed parentheses on {self}, or an unexpected argument was passed"
            )

    def __call__(self, obj: commands.MessageCommand) -> commands.MessageCommand:
        return self._bind(obj)

    def __repr__(self) -> str:
        return f"Check('{self.__class__.__name__}')"

    def _bind(self, obj: commands.MessageCommand) -> commands.MessageCommand:
        """Binds the check to the command object."""
        try:
            obj.add_check(self)
        except AttributeError:
            raise exceptions.BadCheck(
                f"'{obj}' is not a MessageCommand - "
                "move this decorator above the command decorator"
            )

        return obj

    def _raise(self, ctx: context.MessageContext, msg: str) -> None:
        """Raised a `CheckFailed` exception for a command name and with
        the given message
        """
        e = exceptions.CheckFailed(f"{ctx.command} failed - {msg}")
        ctx.exceptions.append(e)
        raise e

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abc.abstractmethod
    async def execute(self, ctx: context.MessageContext) -> None:
        """Executes the check.

        Args:
            ctx: `yami.MessageContext`
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

    async def execute(self, ctx: context.MessageContext) -> None:
        if ctx.author.id not in ctx.bot.owner_ids:
            self._raise(ctx, "you are not the owner of this application")


class is_in_guild(Check):
    """Fails if the command was not run in a guild."""

    __slots__ = ()

    async def execute(self, ctx: context.MessageContext) -> None:
        if not ctx.guild_id:
            self._raise(ctx, "this command can only be run in a guild")


class is_in_dm(Check):
    """Fails if the command was not run in a DM."""

    __slots__ = ()

    async def execute(self, ctx: context.MessageContext) -> None:
        if ctx.guild_id:
            self._raise(ctx, "this command can only be run in a DM")


class has_role(Check):
    """Fails if the author does not have a role with the given name or
    id.

    This is inherently an `is_in_guild` check as well, because a user
    cannot have a role outside of a guild.

    Args:
        role: `str` | `int`
            The name or id of the role the user must have.
    """

    __slots__ = ("_role",)

    def __init__(self, role: str | int) -> None:
        self._role = role

    def _run_check(self, ctx: context.MessageContext, roles: Sequence[hikari.Role]) -> None:
        if not any(self._role == r.name or self._role == r.id for r in roles):
            self._raise(ctx, f"author does not have the required role: '{self._role}'")

    async def execute(self, ctx: context.MessageContext) -> None:
        if not ctx.guild_id:
            return self._raise(
                ctx, f"this command was run in DM but requires the '{self._role}' role"
            )

        else:
            if ctx.shared.has("member_roles"):
                return self._run_check(ctx, ctx.shared.member_roles)

            if ctx.shared.has("member"):
                member_roles = await ctx.shared.member.fetch_roles()
                ctx.shared.member_roles = member_roles
                return self._run_check(ctx, member_roles)

        member = await ctx.rest.fetch_member(ctx.guild_id, ctx.author)
        member_roles = await member.fetch_roles()

        ctx.shared.member = member
        ctx.shared.member_roles = member_roles

        self._run_check(ctx, member_roles)


class has_any_role(Check):
    """Fails if the author does not have any of the role names or ids
    passed to this check.

    This is inherently an `is_in_guild` check as well, because a user
    cannot have a role outside of a guild.

    Args:
        *roles: `str` | `int`
            The names or ids of the roles the user must have at least
            one of.
    """

    __slots__ = ("_roles",)

    def __init__(self, *roles: str | int) -> None:
        self._roles = roles

    def _run_check(
        self,
        ctx: context.MessageContext,
        roles: Sequence[hikari.Role],
        roles_repr: str | int,
    ) -> None:
        if not any(n == r.name or n == r.id for n in self._roles for r in roles):
            self._raise(ctx, f"author does not have any of the required roles: {roles_repr}")

    async def execute(self, ctx: context.MessageContext) -> None:
        roles_repr = ", ".join(f"'{role}'" for role in self._roles)

        if not ctx.guild_id:
            return self._raise(
                ctx,
                "this command was run in DM but requires "
                f"one of the following roles: {roles_repr}",
            )

        else:
            if ctx.shared.has("member_roles"):
                return self._run_check(ctx, ctx.shared.member_roles, roles_repr)

            if ctx.shared.has("member"):
                member_roles = await ctx.shared.member.fetch_roles()
                ctx.shared.member_roles = member_roles

                return self._run_check(ctx, member_roles, roles_repr)

        member = await ctx.rest.fetch_member(ctx.guild_id, ctx.author)
        member_roles = await member.fetch_roles()

        ctx.shared.member = member
        ctx.shared.member_roles = member_roles

        self._run_check(ctx, member_roles, roles_repr)


class has_perms(Check):
    """Fails if the author does not have all of the specified
    permissions.

    This is inherently an `is_in_guild` check as well, because a user
    cannot have permissions outside of a guild.

    Args:
        **perms: `bool`
            Keyword arguments for each of the available hikari
            Permissions.
    """

    __slots__ = ("_perms", "_raw_perms")

    def __init__(self, **perms: bool) -> None:
        self._raw_perms = perms
        self._perms: list[hikari.Permissions] = []

    def _get_perm(self, ctx: context.MessageContext, perm: str) -> hikari.Permissions:
        try:
            p = getattr(hikari.Permissions, perm)
        except AttributeError:
            self._raise(ctx, f"'{perm}' is not a valid permission")
            raise
        else:
            return cast(hikari.Permissions, p)

    async def _run_check(
        self,
        ctx: context.MessageContext,
        perms: list[hikari.Permissions],
    ) -> None:
        missing_perms: list[hikari.Permissions] = []

        if not ctx.shared.has("channel"):
            channel = await ctx.rest.fetch_channel(ctx.channel_id)
            ctx.shared.channel = channel
        else:
            channel = ctx.shared.channel
        assert isinstance(channel, hikari.GuildTextChannel)

        for perm in self._perms:
            for p in channel.permission_overwrites.values():
                if perm in p.deny and perm not in missing_perms:
                    missing_perms.append(perm)

                perms.extend(a for a in p.allow if a not in perms)

            if perm not in perms and perm not in missing_perms:
                missing_perms.append(perm)

        if not missing_perms:
            if all(p in perms for p in self._perms) or hikari.Permissions.ADMINISTRATOR in perms:
                return None

        perm_repr = ", ".join(f"'{p}'" for p in missing_perms)
        self._raise(
            ctx,
            "this command requires the the following "
            f"permissions which were missing: {perm_repr}",
        )

    def _get_perms_for_role(self, role: hikari.Role) -> list[hikari.Permissions]:
        return [*role.permissions]

    def _get_perms_for_roles(self, roles: Sequence[hikari.Role]) -> list[hikari.Permissions]:
        buffer: list[hikari.Permissions] = []

        for role in roles:
            buffer.extend(p for p in self._get_perms_for_role(role) if p not in buffer)

        return buffer

    async def execute(self, ctx: context.MessageContext) -> None:
        perm_repr = ", ".join(f"'{p}'" for p in self._raw_perms)

        if not ctx.guild_id:
            return self._raise(
                ctx,
                f"this command was run in DM but requires the following guild perms: {perm_repr}",
            )

        else:
            for perm, flag in self._raw_perms.items():
                if not flag:
                    continue

                if not hasattr(hikari.Permissions, perm.upper()):
                    return self._raise(ctx, f"command requires an invalid perm: '{perm}'")

                self._perms.append(self._get_perm(ctx, perm.upper()))

            if ctx.shared.has("member_roles"):
                role_perms = self._get_perms_for_roles(ctx.shared.member_roles)

                return await self._run_check(ctx, role_perms)

            if ctx.shared.has("member"):
                member_roles = await ctx.shared.member.fetch_roles()
                role_perms = self._get_perms_for_roles(member_roles)
                ctx.shared.member_roles = member_roles

                return await self._run_check(ctx, role_perms)

        member = await ctx.rest.fetch_member(ctx.guild_id, ctx.author)
        member_roles = await member.fetch_roles()
        ctx.shared.member = member
        ctx.shared.member_roles = member_roles

        role_perms = self._get_perms_for_roles(member_roles)
        await self._run_check(ctx, role_perms)


CustomCheckSigT = Callable[[context.MessageContext], Any]


class custom_check(Check):
    """A custom check. If the check returns `False` or raises an
    `Exception` the check will fail. If the check returns `True` or any
    other value without raising an error, it will pass.

    Args:
        check: `Callable[[yami.MessageContext], Any]`
            The callback function that should be used for the check.

            It should accept one argument of type `yami.MessageContext`
            and return a `bool`.

            This can be an async, or sync function.

    Kwargs:
        message: `str`
            The optional message to use in the `CheckFailed` exception.
            The default message is "a custom check was failed".
    """

    __slots__ = ("_check", "_message")

    def __init__(self, check: CustomCheckSigT | Check, *, message: str = "") -> None:
        self._check = check
        self._message = message

    async def execute(self, ctx: context.MessageContext) -> None:
        message = self._message or "a custom check was failed"

        if isinstance(self._check, Check):
            return await self._check.execute(ctx)

        if inspect.isclass(self._check):
            if issubclass(self._check, Check):
                return await self._check().execute(ctx)  # type: ignore

        else:
            try:
                if inspect.iscoroutinefunction(self._check):
                    result = await self._check(ctx)
                else:
                    result = self._check(ctx)

            except Exception:
                return self._raise(ctx, message)

            if result is False:
                return self._raise(ctx, message)

            return None

        raise exceptions.BadCheck(f"{self} for {ctx.command} is of the wrong type")


class is_the_cutest(Check):
    """Fails if you aren't Jaxtar."""

    __slots__ = ()

    _cutie_id = 135372594953060352

    async def execute(self, ctx: context.MessageContext) -> None:
        if ctx.author.id != self._cutie_id:
            self._raise(ctx, "you are not the cutest")
