import typing as t

__all__: t.List[str] = [
    "Command",
]

class Command:
    """An `Object` representing a `Command`."""
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """The name of this `Command` `Object`."""
        return self._name
