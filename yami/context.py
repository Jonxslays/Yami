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

import hikari

from yami import args as args_
from yami import bot as bot_
from yami import commands, exceptions, utils

__all__ = [
    "MessageContext",
]


class MessageContext:
    """The context surround a message commands invocation.

    Args:
        bot: `yami.Bot`
            The bot instance associated with the context.
        message: `hikari.Message`
            The message associated with the context.
        command: `yami.MessageCommand`
            The command associated with the context.
        prefix: `str`
            The prefix the context with created with.
        *args: `dict[str. yami.MessageArg]`
    """

    __slots__: typing.Sequence[str] = (
        "_message",
        "_command",
        "_bot",
        "_prefix",
        "_exceptions",
        "_shared",
        "_args",
        "_raw_args",
    )

    def __init__(
        self,
        bot: bot_.Bot,
        message: hikari.Message,
        command: commands.MessageCommand,
        prefix: str,
        *,
        raw_args: tuple[inspect.Parameter, ...] = (),
    ) -> None:
        self._message = message
        self._command = command
        self._bot = bot
        self._prefix = prefix
        self._exceptions: list[exceptions.YamiException] = []
        self._shared = utils.Shared()
        self._raw_args = raw_args
        self._args: list[args_.MessageArg] = []

    @property
    def bot(self) -> bot_.Bot:
        """The bot instance associated with the context."""
        return self._bot

    @property
    def author(self) -> hikari.User:
        """The user associated with the context."""
        return self._message.author

    @property
    def cache(self) -> hikari.api.Cache:
        """Shortcut to the bots cache."""
        return self._bot.cache

    @property
    def rest(self) -> hikari.api.RESTClient:
        """Shortcut to the bots rest client."""
        return self._bot.rest

    @property
    def guild_id(self) -> hikari.Snowflake | None:
        """The guild id associated with the context, or None if this
        context was a DMChannel.
        """
        return self._message.guild_id

    @property
    def args(self) -> list[args_.MessageArg]:
        """A list of MessageArguments passed to this context. `self`
        in Module commands and `MessageContext` args will not be present
        here.

        See `raw_args` to get the raw parameters for all args."""
        return self._args

    @property
    def raw_args(self) -> tuple[inspect.Parameter, ...]:
        """A tuple container the raw `inspect.Parameters` that were
        passed to the command. Including self, and this ctx if present.
        """
        return self._raw_args

    @property
    def exceptions(self) -> list[exceptions.YamiException]:
        """Any exceptions that were generated when this context was
        created, including failed check exceptions.
        """
        return self._exceptions

    @property
    def channel_id(self) -> hikari.Snowflake:
        """The channel id associated with the context."""
        return self._message.channel_id

    @property
    def message_id(self) -> hikari.Snowflake:
        """The message id associated with the context."""
        return self._message.id

    @property
    def content(self) -> str:
        """The content of the message associated with the context."""
        # This is checked before the context is created.
        assert self._message.content is not None
        return self._message.content

    @property
    def command(self) -> commands.MessageCommand:
        """The command invoked during the creation of this context."""
        return self._command

    @property
    def message(self) -> hikari.Message:
        """The message associated with this context."""
        return self._message

    @property
    def prefix(self) -> str:
        """The prefix used to create this context."""
        return self._prefix

    @property
    def shared(self) -> utils.Shared:
        """A SharedData object that holds cached information about the
        context that was obtained while checks were run for this
        context.
        """
        return self._shared

    async def respond(self, *args: typing.Any, **kwargs: typing.Any) -> hikari.Message:
        """Respond to the message that created this context.

        Args:
            *args, **kwargs
                The arguments for `hikari.Message.respond`

        Returns:
            hikari.Message
                The message this response creates.
        """
        return await self._message.respond(*args, **kwargs)

    async def getch_member(self) -> hikari.Member | None:
        """Get or fetch the `hikari.Member` object associated with the
        context. This method calls to the cache first, and falls back to
        rest if not found.

        **WARNING**:
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            `hikari.Member` | `None`
                The member object associated with the context, or
                None if the context is a DMChannel.
        """
        if not self._message.guild_id:
            return None

        return self._bot.cache.get_member(
            self._message.guild_id, self._message.author
        ) or await self._bot.rest.fetch_member(self._message.guild_id, self._message.author)

    async def getch_guild(self) -> hikari.Guild | None:
        """Get or fetch the `hikari.Guild` object associated with the
        context. This method calls to the cache first, and falls back to
        rest if not found.

        **WARNING**:
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            `hikari.Guild` | `None`
                The guild object associated with the context, or
                None if the context is a DMChannel.
        """
        if not self._message.guild_id:
            return None

        return self._bot.cache.get_guild(
            self._message.guild_id
        ) or await self._bot.rest.fetch_guild(self._message.guild_id)

    async def getch_channel(self) -> hikari.GuildChannel | hikari.PartialChannel:
        """Get or fetch the `hikari.PartialChannel` object associated
        with the context. This method calls to the cache first, and
        falls back to rest if not found.

        This method can return one of any:
            `DMChannel`, `GroupDMChannel`, `GuildTextChannel`,
            `GuildVoiceChannel`, `GuildStoreChannel`, `GuildNewsChanne`.

        **WARNING**:
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            `hikari.PartialChannel`
                The channel object associated with the context.
        """
        return self._bot.cache.get_guild_channel(
            self._message.channel_id
        ) or await self._bot.rest.fetch_channel(self._message.channel_id)
