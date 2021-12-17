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

import typing

import hikari

__all__: typing.List[str] = [
    "MessageContext",
]

if typing.TYPE_CHECKING:
    from yami import commands
    from yami.bot import Bot


class MessageContext:
    """An object representing a message context.

    Args:
        bot: yami.Bot
            The bot instance associated with the context.
        command: yami.MessageCommand
            The command associated with the context.
        message: hikari.Message
            The message associated with the context.
        prefix: str
            The prefix the context with created with.
    """

    __slots__: typing.Sequence[str] = ("_message", "_command", "_content", "_bot", "_prefix")

    def __init__(
        self,
        bot: Bot,
        content: str,
        message: hikari.Message,
        command: commands.MessageCommand,
        prefix: str,
    ) -> None:
        if not message.content:
            raise ValueError("No content in message. what?")

        self._content = content
        self._message = message
        self._command = command
        self._bot = bot
        self._prefix = prefix

    @property
    def bot(self) -> Bot:
        """The bot instance associated with the context.

        Returns:
            yami.Bot
                The bot instance associated with the context.
        """
        return self._bot

    @property
    def author(self) -> hikari.User:
        """The user associated with the context.

        Returns:
            hikari.User
                The user associated with the context.
        """
        return self._message.author

    @property
    def guild_id(self) -> typing.Optional[hikari.Snowflake]:
        """The guild id associated with the context.

        Returns:
            Optional[hikari.Snowflake]
                The guild id associated with the context or None
                if the Context is a DMChannel.
        """
        return self._message.guild_id

    @property
    def channel_id(self) -> hikari.Snowflake:
        """The channel id associated with the context.

        Returns:
            hikari.Snowflake
                The channel id associated with the context.
        """
        return self._message.channel_id

    @property
    def message_id(self) -> hikari.Snowflake:
        """The message id associated with the context.

        Returns:
            hikari.Snowflake
                The message id associated with the context.
        """
        return self._message.id

    @property
    def content(self) -> str:
        """The content of the message associated with the context.

        Returns:
            str
                The content
        """
        return self._content

    @property
    def command(self) -> commands.MessageCommand:
        """The command used to generate this context.

        Returns:
            yami.MessageCommand
                The command that was invoked.
        """
        return self._command

    @property
    def message(self) -> hikari.Message:
        """The message associated with this context.

        Returns:
            hikari.Message
                The message.
        """
        return self._message

    @property
    def prefix(self) -> str:
        """The prefix this context was created with.

        Returns:
            str
                The prefix used.
        """
        return self._prefix

    async def respond(
        self,
        content: hikari.UndefinedOr[typing.Any] = hikari.UNDEFINED,
        *,
        attachment: hikari.UndefinedOr[hikari.Resourceish] = hikari.UNDEFINED,
        attachments: hikari.UndefinedOr[typing.Sequence[hikari.Resourceish]] = hikari.UNDEFINED,
        component: hikari.UndefinedOr[hikari.api.ComponentBuilder] = hikari.UNDEFINED,
        components: hikari.UndefinedOr[
            typing.Sequence[hikari.api.ComponentBuilder]
        ] = hikari.UNDEFINED,
        embed: hikari.UndefinedOr[hikari.Embed] = hikari.UNDEFINED,
        embeds: hikari.UndefinedOr[typing.Sequence[hikari.Embed]] = hikari.UNDEFINED,
        nonce: hikari.UndefinedOr[str] = hikari.UNDEFINED,
        tts: hikari.UndefinedOr[bool] = hikari.UNDEFINED,
        reply: hikari.UndefinedOr[hikari.SnowflakeishOr[hikari.PartialMessage]] = hikari.UNDEFINED,
        mentions_everyone: hikari.UndefinedOr[bool] = hikari.UNDEFINED,
        mentions_reply: hikari.UndefinedOr[bool] = hikari.UNDEFINED,
        user_mentions: hikari.UndefinedOr[
            hikari.SnowflakeishSequence[hikari.PartialUser] | bool
        ] = hikari.UNDEFINED,
        role_mentions: hikari.UndefinedOr[
            hikari.SnowflakeishSequence[hikari.PartialRole] | bool
        ] = hikari.UNDEFINED,
    ) -> hikari.Message:
        return await self._message.respond(
            content,
            attachment=attachment,
            attachments=attachments,
            component=component,
            components=components,
            embed=embed,
            embeds=embeds,
            nonce=nonce,
            tts=tts,
            reply=reply,
            mentions_everyone=mentions_everyone,
            mentions_reply=mentions_reply,
            user_mentions=user_mentions,
            role_mentions=role_mentions,
        )

    async def getch_guild(self) -> typing.Optional[hikari.Guild]:
        """Get or fetch the `hikari.Guild` object associated with the
        context. This method calls to the cache first, and falls back to
        rest if not found.

        **WARNING**:
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            Optional[hikari.Guild]
                The guild object associated with the context, or
                None if the context is a DMChannel.
        """
        if not self.guild_id:
            return None

        return self.bot.cache.get_guild(self.guild_id) or await self.bot.rest.fetch_guild(
            self.guild_id
        )

    async def getch_channel(self) -> hikari.GuildChannel | hikari.PartialChannel:
        """Get or fetch the `hikari.PartialChannel` object associated
        with the context. This method calls to the cache first, and
        falls back to rest if not found.

        This method can return one of any:
            DMChannel, GroupDMChannel, GuildTextChannel,
            GuildVoiceChannel, GuildStoreChannel, GuildNewsChannel.

        **WARNING**:
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            hikari.PartialChannel
                The channel object associated with the context.
        """
        return self.bot.cache.get_guild_channel(
            self.channel_id
        ) or await self.bot.rest.fetch_channel(self.channel_id)
