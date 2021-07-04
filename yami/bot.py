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
        prefix (Callable[..., Union[List[str], str]], Union[List[str], str): The command prefix the `Bot` should respond to.

        shun_bots (bool, optional): Whether or not the `Bot` should shun it's own kind.
            Defaults to True. (The `Bot` will ignore commands invoked by bots.)

        owners (Iterable[int], optional): An iterable of integers representing the `Bot`'s owners ID's.

        case_insensitive (bool, optional): Check case during command invokations.
            Defaults to True. (Commands are invoked regardless of case.)

        **kwargs: Remaining arguments passed to `hikari.BotApp`.
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
        self._commands: t.MutableMapping[str, yami.Command] = {}
        self._aliases: t.MutableMapping[str, yami.Command] = {}
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
    def aliases(self) -> set[str]:
        """A Set containing all `Command` aliases."""
        return set(self._aliases.keys())

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

    def command(self, **kwargs: t.Any) -> t.Callable[..., t.Any]:
        """Decorator used to instantiate a new `Command`."""
        def predicate(callback: t.Callable[..., t.Any]) -> yami.Command:
            return self.add_command(callback, **kwargs)

        return predicate

    def add_command(self, callback: t.Union[t.Callable[..., t.Any], yami.Command], **kwargs: t.Any) -> yami.Command:
        """Registers a `Command` to the `Bot`."""
        if not isinstance(callback, yami.Command):
            callback_cmd = yami.Command(
                callback, name=kwargs.get("name", callback.__name__),
                aliases=kwargs.get("aliases", []), hidden=kwargs.get("hidden", False),
            )

        if self.case_insensitive:
            callback_cmd._name = callback_cmd.name.lower()
            callback_cmd._aliases = [a.lower() for a in callback_cmd._aliases]

        if callback_cmd.name in (c.name for c in self.commands):
            raise yami.CommandAlreadyRegistered(
                f"Command name already registered: {callback_cmd.name}."
            )

        if (x := set(callback_cmd.aliases) & self.aliases):
            raise yami.CommandAlreadyRegistered(
                f"Command already registered with alias: {x}"
            )

        if callback_cmd.aliases:
            for a in callback_cmd.aliases:
                self._aliases[a] = callback_cmd

        # TODO optimize the above if statements.

        self._commands[callback_cmd.name] = callback_cmd
        return self._commands[callback_cmd.name]

    def get_command(self, name: str) -> t.Optional[yami.Command]:
        """Method used to get a `Command` Object from the `Bot`.
        Returns `None` if one is not found with this `name`."""
        if self.case_insensitive:
            name = name.lower()

        if name in self._commands:
            return self._commands[name]

        if name in self.aliases:
            return self._aliases[name]

        return None
