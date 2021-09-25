import abc
import typing

import hikari

from yami import bot, commands

__all__: typing.List[str] = [
    "AbstractContext",
    "LegacyContext",
]


class AbstractContext(type, abc.ABC):
    """The base class all command context's will inherit from.

    Args:

    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractproperty
    def bot(self) -> bot.Bot:
        """The bot instance associated with the context.

        Returns:
            yami.Bot
                The bot instance associated with the context.
        """
        ...

    @property
    @abc.abstractproperty
    def author(self) -> hikari.User:
        """The user associated with the context.

        Returns:
            hikari.User
                The user associated with the context.
        """
        ...

    @property
    @abc.abstractproperty
    def guild_id(self) -> typing.Optional[hikari.Snowflake]:
        """The guild id associated with the context.

        Returns:
            typing.Optional[hikari.Snowflake]
                The guild id associated with the context or None
                if the Context is a DMChannel.
        """
        ...

    @property
    @abc.abstractproperty
    def channel_id(self) -> hikari.Snowflake:
        """The channel id associated with the context.

        Returns:
            hikari.Snowflake
                The channel id associated with the context.
        """
        ...

    @property
    @abc.abstractproperty
    def message_id(self) -> hikari.Snowflake:
        """The message id associated with the context.

        Returns:
            hikari.Snowflake
                The message id associated with the context.
        """
        ...

    @abc.abstractmethod
    async def grab_guild(self) -> typing.Optional[hikari.Guild]:
        """Grabs the `hikari.Guild` object associated with the context.
        This method calls to the cache first, and falls back to rest if
        not found.

        **WARNING**:
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            typing.Optiona[hikari.Guild]
                The guild object associated with the context, or
                None if the context is a DMChannel.
        """
        ...

    @abc.abstractmethod
    async def grab_message(self) -> hikari.Message:
        """Grabs the `hikari.Message` object associated with the
        context. This method calls to the cache first, and falls back
        to rest if not found.

        **WARNING**:
            This method can utilize both cache, and rest. For more fine
            grained control consider using cache or rest yourself
            explicitly.

        Returns:
            hikari.Message
                The message object associated with the context.
        """
        ...

    @abc.abstractmethod
    async def grab_channel(self) -> hikari.PartialChannel:
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
        ...


class LegacyContext(metaclass=AbstractContext):
    """An object representing a legacy context. A `boomer` command
    handler, if you will.

    Args:
        bot: yami.Bot
            The bot instance associated with the context.
        command: yami.AbstractCommand
            The command associated with the context.
        message: hikari.Message
            The message associated with the context.
    """

    __slots__: typing.Sequence[str] = ("_message", "_command", "_content")

    def __init__(
        self,
        bot: bot.Bot,
        content: str,
        message: hikari.Message,
        *,
        command: commands.LegacyCommand,
    ) -> None:
        if not message.content:
            raise ValueError("No content in message. what?")

        self._content = content
        self._message = message
        self._command = command
        self._bot = bot

    @property
    def bot(self) -> bot.Bot:
        return self._bot

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
