import typing as t

import hikari
import yami

__all__: t.List[str] = [
    "Bot",
]


class Bot(hikari.BotApp):
    """An `Object` that inherits from `hikari.BotApp` and adds
    an additional API overlay to easily implement and handle commands.

    Args:
        prefix (str): The command prefix the `Bot` should respond to.

        shun_bots (bool, optional): Whether or not the `Bot` should shun it's own kind.
            Defaults to True. (The `Bot` will ignore commands invoked by bots.)

        owners (iterable[int], optional): An iterable of integers representing the `Bot`'s owners ID's.

        case_insensitive (bool, optional): Check case during command invokations.
            Defaults to True. (Commands are invoked regardless of case.)

        **kwargs: Remaining arguments passed to `hikari.BotApp`.
    """

    __slots__: t.Sequence[str] = (
        "_prefix", "_shun_bots", "_case_insensitive",
        "_owners", "_commands", "_modules",
    )

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
        self._commands: t.MutableMapping[str, yami.Command] = {}
        self._modules: t.MutableMapping[str, yami.Module] = {}

    @property
    def modules(self) -> set[yami.Module]:
        """A set containing all `Modules`s registered to the `Bot` (Only includes loaded `Module`s)."""
        return set(self._modules.values())

    @property
    def commands(self) -> set[yami.Command]:
        """A Set containing all `Command`s registered to the `Bot`."""
        return set(self._commands.values())

    @property
    def prefix(self) -> t.Union[t.Callable[..., str], str]:
        """The `Command` prefix the `Bot` should respond to."""
        return self._prefix

    @property
    def shun_bots(self) -> bool:
        """Whether or not the `Bot` should shun it's own kind."""
        return self._shun_bots

    @property
    def case_insensitive(self) -> bool:
        """Check case during command invokations."""
        return self._case_insensitive

    @property
    def owners(self) -> t.Iterable[int]:
        """An iterable containing the Owner ID's of the `Bot`."""
        return self._owners
