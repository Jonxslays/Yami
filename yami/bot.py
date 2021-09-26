import concurrent.futures
import typing

import hikari

from yami import commands

__all__: typing.List[str] = ["Bot"]


class Bot(hikari.GatewayBot):
    """A subclass of `hikari.GatewayBot` that provides an interface
    for handling commands.

    This is the class you will instantiate, to utilize command features
    on top of the `hikari.GatewayBot` superclass.

    Args:
        token: str
            The bot token to sign in with.
        prefix: typing.Union[str, typing.Sequence[str]]
            The prefix, or sequence of prefixes to listen for.
            Planned support for mentions, and functions soon (tm).
        message_subscription: bool
            Whether or not to subscribe to `hikari.MessageCreateEvent`.
            Defaults to True. Set this to False if you only plan to
            utilize slash commands.
        owner_ids: typing.Optional[typing.Sequence[int]]
            A sequence of integers representing the Snowflakes of the
            bots owners.
        **kwargs: typing.Any
            The remaining kwargs for `hikari.GatewayBot`.
    """

    __slots__: typing.Sequence[str] = (
        "_prefix",
        "_case_insensitive",
        "_owner_ids",
        "_commands",
        "_aliases",
    )

    def __init__(
        self,
        token: str,
        *,
        prefix: typing.Union[str, typing.Sequence[str]],
        case_insensitive: bool = True,
        message_subscription: bool = True,
        owner_ids: typing.Optional[typing.Sequence[int]] = None,
        allow_color: bool = True,
        banner: typing.Optional[str] = "hikari",
        executor: typing.Optional[concurrent.futures.Executor] = None,
        force_color: bool = False,
        cache_settings: typing.Optional[hikari.CacheSettings] = None,
        http_settings: typing.Optional[hikari.HTTPSettings] = None,
        intents: hikari.Intents = hikari.Intents.ALL_UNPRIVILEGED,
        logs: typing.Union[None, int, str, typing.Dict[str, typing.Any]] = "INFO",
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: typing.Optional[hikari.ProxySettings] = None,
        rest_url: typing.Optional[str] = None,
    ) -> None:
        super().__init__(
            token,
            allow_color=allow_color,
            banner=banner,
            executor=executor,
            force_color=force_color,
            cache_settings=cache_settings,
            http_settings=http_settings,
            intents=intents,
            logs=logs,
            max_rate_limit=max_rate_limit,
            max_retries=max_retries,  # will be implemented in dev102
            proxy_settings=proxy_settings,
            rest_url=rest_url,
        )

        # Validate the prefix
        if isinstance(prefix, str):
            self._prefix: typing.Sequence[str] = (prefix,)

        elif isinstance(prefix, typing.Sequence):
            if not prefix:
                raise ValueError(f"The sequence passed to prefix was of length 0.")

            if not all(isinstance(p, str) for p in prefix):
                raise TypeError(f"One or more items passed to prefix were not of {repr(str)}.")

            if not all(bool(p) for p in prefix):
                raise ValueError("One or more items passed to prefix were of length 0.")

            self._prefix = prefix

        else:
            raise TypeError(f"{type(prefix)} is an unsupported type for 'prefix'.")

        self._owner_ids = owner_ids
        self._case_insensitive = case_insensitive

        if message_subscription:
            self.event_manager.subscribe(hikari.MessageCreateEvent, self.watch_for_commands)

        self._commands: typing.MutableMapping[str, commands.LegacyCommand] = {}
        self._aliases: typing.MutableMapping[str, str] = {}

    def add_command(
        self,
        command: typing.Union[typing.Callable[..., typing.Any], commands.LegacyCommand],
        *,
        name: typing.Optional[str] = None,
    ) -> commands.LegacyCommand:

        if isinstance(command, commands.LegacyCommand):
            self._commands[command.name] = command
            return self._commands[command.name]

        name = command.__name__ if not name else name
        new_cmd = commands.LegacyCommand.new(command, name)
        self._commands[name] = new_cmd

        return new_cmd

    async def watch_for_commands(self, event: hikari.MessageCreateEvent) -> None:
        if not event.message.content:
            return None

        # if event.message.content.startswith(self._prefix):
        #     pass
