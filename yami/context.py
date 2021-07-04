import typing as t

import hikari

import yami

__all__: t.List[str] = [
    "Context",
]

class Context:
    """An `Object` representing the `Context` that a `Command` was invoked in."""

    def __init__(
        self, bot: yami.Bot, message: hikari.Message, prefix: str,
        invoked_with: t.Optional[str], command: yami.Command, args: t.List[t.Any]
    ) -> None:
        self._bot = bot
        self._message = message
        self._prefix = prefix
        self._invoked_with = invoked_with
        self._command = command
        self._args = args

    @property
    def bot(self) -> yami.Bot:
        """The `Bot` `Object` the `Command` was invoked from."""
        return self._bot

    @property
    def message(self) -> hikari.Message:
        """The `Message` that invoked the command."""
        return self._message

    @property
    def message_id(self) -> hikari.Snowflake:
        """The ID of the `Message` the `Command` was invoked with."""
        return self.message.id

    @property
    def prefix(self) -> str:
        """The prefix that invoked the command."""
        return self._prefix

    @property
    def invoked_with(self) -> t.Optional[yami.Command]:
        """The `Command` that was invoked. """
        return self._command

    @property
    def args(self) -> t.List[t.Any]:
        """A `List` of arguments passed to the command"""
        return self._args

    @property
    def author(self) -> hikari.User:
        """Returns the `User` that invoked the `Command`."""
        return self.message.author

    @property
    def channel_id(self) -> hikari.Snowflake:
        """The ID of the `TextChannel` the `Command` was invoked in."""
        return self.message.channel_id

    @property
    async def channel(self) -> t.Union[hikari.GuildChannel, hikari.PartialChannel, hikari.TextChannel]:
        """Returns the `TextChannel` the `Command` was invoked in.
        Calls the API using fetch, if the channel isn't cached."""
        if get_chan := self.bot.cache.get_guild_channel(self.channel_id):
            return get_chan

        if fetch_chan := await self.bot.rest.fetch_channel(self.channel_id):
            return fetch_chan

        raise yami.ChannelNotFound(f"No Channel was found with ID: {self.channel_id}.")
