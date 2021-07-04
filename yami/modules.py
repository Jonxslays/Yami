import typing as t

__all__: t.List[str] = [
    "Module",
]


class Module:
    """An `Object` representing a `Module`, used for encapsulating similar `Command`s."""
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """The name of this `Module` `Object`."""
        return self._name
