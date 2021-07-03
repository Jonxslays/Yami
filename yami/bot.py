import concurrent
import typing as t

import hikari

from yami import commands


class Bot(hikari.BotApp):
    """An object that inherits from hikari.impl.bot.BotApp and adds
    an additional API overlay to easily implement and handle commands.

    Args:
        prefix (str): The command prefix the Bot should respond to.

        shun_bots (bool, optional): Whether or not the Bot should shun it's own kind.
            Defaults to True. (The bot will ignore commands invoked by bots.)

        owners (iterable[int], optional): An iterable of integers representing the bot's owners ID's.

        case_insensitive (bool, optional): Check case during command invokations.
            Defaults to True. (Commands are invoked regardless of case.)

        **kwargs: Remaining arguments passed to hikari.BotApp.
    """

    def __init__(
        self,
        prefix: t.Union[t.Callable[..., str], str],
        *,
        shun_bots: bool = True,
        owners: t.Iterable[int] = (),
        case_insensitive: bool = True,
        **kwargs: t.Any
    ) -> None:
        super().__init__(**kwargs)
        self._prefix = prefix
        self._shun_bots = shun_bots
        self._case_insensitive = case_insensitive
        self._owners = owners

    @property
    def prefix(self) -> t.Union[t.Callable[..., str], str]:
        """The command prefix the Bot should respond to."""
        return self._prefix

    @property
    def shun_bots(self) -> bool:
        """Whether or not the Bot should shun it's own kind."""
        return self._shun_bots

    @property
    def case_insensitive(self) -> bool:
        """Check case during command invokations."""
        return self._case_insensitive

    @property
    def owners(self) -> t.Iterable[int]:
        """An iterable containing the Owner ID's of the bot."""
        return self._owners
