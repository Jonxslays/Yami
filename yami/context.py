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
"""Module containing Context objects."""

from __future__ import annotations

import abc
import asyncio
import typing

import hikari

from yami import args as args_
from yami import bot as bot_
from yami import commands, utils

if typing.TYPE_CHECKING:
    from hikari.api import special_endpoints

__all__ = ["Context", "MessageContext"]


class Context(abc.ABC):
    """Base Context all Yami contexts inherit from."""

    __slots__ = ()

    def __init__(
        self,
        bot: bot_.Bot,
        message: hikari.Message,
        command: commands.MessageCommand,
        prefix: str,
        invoked_subcommands: list[commands.MessageCommand] = [],
    ) -> None:
        ...

    @property
    @abc.abstractmethod
    def bot(self) -> bot_.Bot:
        """The bot instance associated with this context."""
        ...

    @property
    @abc.abstractmethod
    def author(self) -> hikari.User:
        """The user that created this context."""
        ...

    @property
    @abc.abstractmethod
    def cache(self) -> hikari.api.Cache:
        """Shortcut to the bots cache."""
        ...

    @property
    @abc.abstractmethod
    def rest(self) -> hikari.api.RESTClient:
        """Shortcut to the bots rest client."""
        ...

    @property
    @abc.abstractmethod
    def guild_id(self) -> hikari.Snowflake | None:
        """The guild id associated with the context, or ``None`` if this
        context was a :obj:`~hikari.DMChannel`.
        """
        ...

    @property
    @abc.abstractmethod
    def args(self) -> list[args_.MessageArg]:
        """A list of converted :obj:`~yami.MessageArgs` passed to this
        context. Context will not be present here even though it was
        passed to the command callback.

        .. note::
            If this context was invoked with subcommands and parent
            commands, only the final subcommands args will be present
            here.
        """
        ...

    @property
    @abc.abstractmethod
    def exceptions(self) -> list[Exception]:
        """Any exceptions that were generated when this context was
        created, including failed check exceptions.
        """
        ...

    @property
    @abc.abstractmethod
    def channel_id(self) -> hikari.Snowflake:
        """The channel id this context was created in."""
        ...

    @property
    @abc.abstractmethod
    def message(self) -> hikari.Message:
        """The message associated with this context."""
        ...

    @property
    @abc.abstractmethod
    def message_id(self) -> hikari.Snowflake:
        """The message id of this contexts message."""
        ...

    @property
    @abc.abstractmethod
    def content(self) -> str:
        """The content of the message associated with the context."""
        # This is checked before the context is created.
        ...

    @property
    @abc.abstractmethod
    def command(self) -> commands.MessageCommand:
        """The command invoked during the creation of this context."""
        ...

    @property
    @abc.abstractmethod
    def shared(self) -> utils.Shared:
        """A :obj:`~yami.Shared` object that can be used to share data
        between subcommands.

        .. hint::
            Also houses cached data from the checks that were run for
            this context.
        """
        ...


class MessageContext(Context):
    """The context surrounding a message commands invocation.

    Args:
        bot (:obj:`~yami.Bot`): The bot instance associated with the
            context.
        message (:obj:`hikari.Message`): The message that created this
            context.
        command (:obj:`yami.MessageCommand`): The command that was
            invoked to create this context.
        prefix (:obj:`str`): The prefix that was used to create this
            context.
    """

    __slots__: typing.Sequence[str] = (
        "_message",
        "_command",
        "_bot",
        "_prefix",
        "_exceptions",
        "_shared",
        "_args",
        "_invoked_subcommands",
    )

    def __init__(
        self,
        bot: bot_.Bot,
        message: hikari.Message,
        command: commands.MessageCommand,
        prefix: str,
        invoked_subcommands: list[commands.MessageCommand] = [],
    ) -> None:
        self._message = message
        self._command = command
        self._bot = bot
        self._prefix = prefix
        self._exceptions: list[Exception] = []
        self._shared = utils.Shared()
        self._args: list[args_.MessageArg] = []
        self._invoked_subcommands = invoked_subcommands

    @property
    def bot(self) -> bot_.Bot:
        """The bot instance associated with this context."""
        return self._bot

    @property
    def author(self) -> hikari.User:
        """The user that created this context."""
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
        """The guild id associated with the context, or ``None`` if this
        context was a :obj:`~hikari.DMChannel`.
        """
        return self._message.guild_id

    @property
    def args(self) -> list[args_.MessageArg]:
        """A list of converted :obj:`~yami.MessageArgs` passed to this
        context. Context will not be present here even though it was
        passed to the command callback.

        .. note::
            If this context was invoked with subcommands and parent
            commands, only the final subcommands args will be present
            here.
        """
        return self._args

    @property
    def exceptions(self) -> list[Exception]:
        """Any exceptions that were generated when this context was
        created, including failed check exceptions.
        """
        return self._exceptions

    @property
    def channel_id(self) -> hikari.Snowflake:
        """The channel id this context was created in."""
        return self._message.channel_id

    @property
    def message(self) -> hikari.Message:
        """The message associated with this context."""
        return self._message

    @property
    def message_id(self) -> hikari.Snowflake:
        """The message id of this contexts message."""
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
    def prefix(self) -> str:
        """The prefix used to create this context."""
        return self._prefix

    @property
    def shared(self) -> utils.Shared:
        """A :obj:`~yami.Shared` object that can be used to share data
        between subcommands.

        .. hint::
            Also houses cached data from the checks that were run for
            this context.
        """
        return self._shared

    @property
    def invoked_subcommands(self) -> list[commands.MessageCommand]:
        """The subcommands that were invoked with this context, or
        ``None`` if there were none.

        .. note::
            If subcommands were chained and the parent callback was not
            actually run (due to having ``invoke_with`` set to
            ``False``) it will not appear here.
        """
        return self._invoked_subcommands

    def trigger_typing(self) -> special_endpoints.TypingIndicator:
        """Shortcut method to ``ctx.rest.trigger_typing`` in the current
        channel.

        .. code-block:: python

            async with ctx.trigger_typing():
                # do work here and typing will stop
                # when the context manager is exited.

        Returns:
            :obj:`~hikari.api.special_endpoints.TypingIndicator`: An
            async context manager for the typing indicator on Discord.
        """
        return self._bot.rest.trigger_typing(self._message.channel_id)

    def iter_arg_values(self) -> typing.Generator[typing.Any, None, None]:
        """Iterates the contexts message args.

        Returns:
            :obj:`~typing.Generator`: A generator over the arguments.

        Yields:
            :obj:`~typing.Any`: Each argument.
        """
        yield from (v.value for v in self._args)

    async def respond(
        self,
        content: hikari.UndefinedOr[typing.Any],
        *,
        delete_after: int | None = None,
        **kwargs: typing.Any,
    ) -> hikari.Message:
        """Respond to the message that created this context.

        Args:
            content (:obj:`~typing.Any`): The content of this response.

        Keyword Args:
            delete_after (:obj:`int` | :obj:`None`): The optional length
                of time to delete this message after (in seconds).
            **kwargs (:obj:`~typing.Any`): The remaining kwargs passed
                to the ``hikari.Message.respond`` method.

        Returns:
            :obj:`~hikari.messages.Message`: The message this response
            created.
        """
        msg = await self._message.respond(content, **kwargs)

        if delete_after is not None:

            async def cleanup(timeout: int) -> None:
                await asyncio.sleep(timeout)

                try:
                    await msg.delete()
                except hikari.NotFoundError:
                    pass

            asyncio.create_task(cleanup(delete_after))

        return msg

    async def getch_member(self) -> hikari.Member | None:
        """Get or fetch the :obj:`hikari.Member` object associated with
        the context. This method calls to the cache first, and falls
        back to rest if not found.

        .. warning::
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            :obj:`~hikari.guilds.Member` | :obj:`None`: The member
            object associated with this context, or :obj:`None` if the
            context is a :obj:`~hikari.channels.DMChannel`.
        """
        if not self._message.guild_id:
            return None

        return self._bot.cache.get_member(
            self._message.guild_id, self._message.author
        ) or await self._bot.rest.fetch_member(self._message.guild_id, self._message.author)

    async def getch_guild(self) -> hikari.Guild | None:
        """Get or fetch the :obj:`hikari.guilds.Guild` object associated
        with the context. This method calls to the cache first, and
        falls back to rest if not found.

        .. warning::
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            :obj:`~hikari.guilds.Guild` | :obj:`None`: The guild object
            associated with this context, or :obj:`None` if the context
            is a :obj:`~hikari.channels.DMChannel`.
        """
        if not self._message.guild_id:
            return None

        return self._bot.cache.get_guild(
            self._message.guild_id
        ) or await self._bot.rest.fetch_guild(self._message.guild_id)

    async def getch_channel(self) -> hikari.GuildChannel | hikari.PartialChannel:
        """Get or fetch the :obj:`hikari.channels.PartialChannel` object
        associated with the context. This method calls to the cache
        first, and falls back to rest if not found.

        .. note::
            This method can return any of the following:

            :obj:`~hikari.channels.DMChannel`,
            :obj:`~hikari.channels.GroupDMChannel`,
            :obj:`~hikari.channels.GuildTextChannel`,
            :obj:`~hikari.channels.GuildVoiceChannel`,
            :obj:`~hikari.channels.GuildStoreChannel`,
            :obj:`~hikari.channels.GuildNewsChannel`.

        .. warning::
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            :obj:`~hikari.channels.PartialChannel`: The channel object
            associated with this context.
        """
        return self._bot.cache.get_guild_channel(
            self._message.channel_id
        ) or await self._bot.rest.fetch_channel(self._message.channel_id)
