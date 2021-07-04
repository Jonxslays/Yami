class Command:
    """An Object representing a Command."""
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        """The name of this command Object."""
        return self._name
