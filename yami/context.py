from __future__ import annotations

import typing

import hikari

__all__: typing.List[str] = [
    "LegacyContext",
]

if typing.TYPE_CHECKING:
    from yami import commands
    from yami.bot import Bot


class LegacyContext:
    """An object representing a legacy context. A `boomer` context,
    the old school, cancelled by discord.

    Args:
        bot: yami.Bot
            The bot instance associated with the context.
        command: yami.LegacyCommand
            The command associated with the context.
        message: hikari.Message
            The message associated with the context.
    """

    __slots__: typing.Sequence[str] = ("_message", "_command", "_content", "_bot")

    def __init__(
        self,
        bot: Bot,
        content: str,
        message: hikari.Message,
        command: commands.LegacyCommand,
    ) -> None:
        if not message.content:
            raise ValueError("No content in message. what?")

        self._content = content
        self._message = message
        self._command = command
        self._bot = bot

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
        return self._content

    @property
    def command(self) -> commands.LegacyCommand:
        return self._command

    @property
    def message(self) -> hikari.Message:
        return self._message

    async def respond(self, content: str) -> hikari.Message:
        return await self._message.respond(content)

    async def get_or_fetch_guild(self) -> typing.Optional[hikari.Guild]:
        """Grabs the `hikari.Guild` object associated with the context.
        This method calls to the cache first, and falls back to rest if
        not found.

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
            return

        return self.bot.cache.get_guild(self.guild_id) or await self.bot.rest.fetch_guild(
            self.guild_id
        )

    async def get_or_fetch_channel(self) -> hikari.GuildChannel | hikari.PartialChannel:
        """Grabs the `hikari.PartialChannel` object associated with the
        Context. This method calls to the cache first, and falls back to
        rest if not found.

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
