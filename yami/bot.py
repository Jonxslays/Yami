from __future__ import annotations

import concurrent.futures
import typing

import hikari

from yami import commands as commands_
from yami import context, exceptions

__all__: list[str] = ["Bot"]


class Bot(hikari.GatewayBot):
    """A subclass of `hikari.GatewayBot` that provides an interface
    for handling commands.

    This is the class you will instantiate, to utilize command features
    on top of the `hikari.GatewayBot` superclass.

    Args:
        token: str
            The bot token to sign in with.

    Other Args:
        prefix: Union[str, Sequence[str]]
            The prefix, or sequence of prefixes to listen for.
            Planned support for mentions, and functions soon (tm).
        case_insensitive: bool
            Whether or not to ignore case when handling legacy command
            invocations. Defaults to True.
        owner_ids: Optional[Sequence[int]]
            A sequence of integers representing the Snowflakes of the
            bots owners.
        allow_color : bool
        banner : Optional[str]
        executor : Optional[concurrent.futures.Executor]
        force_color : bool
        cache_settings : Optional[hikari.CacheSettings]
        http_settings : Optional[hikari.HTTPSettings]
        intents : hikari.Intents
        logs : Union[None, LoggerLevel, Dict[str, Any]]
        max_rate_limit : float
        max_retries : Optional[int]
        proxy_settings : Optional[hikari.ProxySettings]
        rest_url : Optional[str]
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
        prefix: str | typing.Sequence[str],
        case_insensitive: bool = True,
        owner_ids: typing.Sequence[int] | None = None,
        allow_color: bool = True,
        banner: str | None = "hikari",
        executor: concurrent.futures.Executor | None = None,
        force_color: bool = False,
        cache_settings: hikari.CacheSettings | None = None,
        http_settings: hikari.HTTPSettings | None = None,
        intents: hikari.Intents = hikari.Intents.ALL_UNPRIVILEGED,
        logs: int | str | dict[str, typing.Any] | None = "INFO",
        max_rate_limit: float = 300,
        max_retries: int = 3,
        proxy_settings: hikari.ProxySettings | None = None,
        rest_url: str | None = None,
    ) -> None:
        self._token: str
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
            max_retries=max_retries,
            proxy_settings=proxy_settings,
            rest_url=rest_url,
        )

        # Validate the prefix
        if isinstance(prefix, str):
            self._prefix: typing.Sequence[str] = (prefix,)

        elif isinstance(prefix, typing.Sequence):  # type: ignore
            if not prefix:
                raise ValueError(f"The sequence passed to prefix was of length 0.")

            if not all(isinstance(p, str) for p in prefix):  # type: ignore
                raise TypeError(f"One or more items passed to prefix were not of {repr(str)}.")

            if not all(bool(p) for p in prefix):
                raise ValueError("One or more items passed to prefix were of length 0.")

            self._prefix = prefix

        else:
            raise TypeError(f"{type(prefix)} is an unsupported type for 'prefix'.")

        self._aliases: dict[str, str] = {}
        self._case_insensitive = case_insensitive
        self._commands: dict[str, commands_.LegacyCommand] = {}
        self._owner_ids = owner_ids

        self.event_manager.subscribe(hikari.MessageCreateEvent, self._listen)

    @property
    def commands(self) -> dict[str, commands_.LegacyCommand]:
        """A dictionary of name, LegacyCommand pairs associated with the
        bot.
        """
        return self._commands

    @property
    def aliases(self) -> dict[str, str]:
        """A dictionary of aliases to their corresponding
        LegacyCommand's name.
        """
        return self._aliases

    def add_command(
        self,
        command: typing.Callable[..., typing.Any] | commands_.LegacyCommand,
        *,
        name: str | None = None,
        aliases: typing.Iterable[str] = [],
    ) -> commands_.LegacyCommand:

        if isinstance(command, commands_.LegacyCommand):
            self._commands[command.name] = command

            if type(command.aliases) not in (list, tuple):
                raise exceptions.BadAlias(
                    f"Aliases must be a list or tuple of strings, not: `{type(command.aliases)}`."
                )

            for a in command.aliases:
                self._aliases[a] = command.name

            return self._commands[command.name]

        name = name if name else command.__name__
        cmd = commands_.LegacyCommand(command, name, aliases)

        return self.add_command(cmd)

    def get_command(self, name: str) -> commands_.LegacyCommand | None:
        return self.commands.get(name)

    async def _listen(self, e: hikari.MessageCreateEvent) -> None:
        if not e.message.content:
            return

        for p in self._prefix:
            if e.message.content.startswith(p):
                return await self._invoke(p, e, e.message.content)

    async def _invoke(self, p: str, event: hikari.MessageCreateEvent, content: str) -> None:
        """Attempts to invoke a command."""
        parsed = content.split(" ")
        name = parsed[0][len(p) :]

        if name in self._aliases:
            cmd = self._commands[self._aliases[name]]
        elif name in self._commands:
            cmd = self._commands[name]
        else:
            raise exceptions.CommandNotFound(f"No command found with name: `{name}`")

        if isinstance(cmd, commands_.LegacyCommand):  # type: ignore
            ctx = context.LegacyContext(self, content, event.message, cmd)
        else:
            raise RuntimeError("Something went wrong")

        await cmd.callback(ctx, *parsed[1:])
