import typing as t

__all__: t.List[str] = [
    "Command",
]

class Command:
    """An `Object` representing a `Command`."""

    __slots__: t.Sequence[str] = (
        "_callback", "_name", "_aliases","_hidden",
    )

    def __init__(
        self, callback: t.Callable[..., t.Any],
        name: str, aliases: t.List[str] = [],
        hidden: bool = False,
    ) -> None:
        self._callback = callback
        self._name = name
        self._aliases = aliases
        self._hidden = hidden

    @property
    def callback(self) -> t.Callable[..., t.Any]:
        """The callback function associated with the `Command`."""
        return self._callback

    @property
    def name(self) -> str:
        """The name of this `Command` `Object`."""
        return self._name

    @property
    def hidden(self) -> bool:
        """Boolean representing whether a `Command` is hidden or not."""
        return self._hidden

    @property
    def aliases(self) -> t.List[str]:
        """A Set of `Command` aliases."""
        return self._aliases
