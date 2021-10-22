from __future__ import annotations

import typing

__all__: typing.List[str] = [
    "LegacyCommand",
]


class LegacyCommand:
    """An object that represents a legacy message content command.

    Args:
        callback:
    """

    __slots__: typing.Sequence[str] = (
        "_callback",
        "_name",
    )

    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        name: str,
    ) -> None:
        self._callback = callback
        self._name = name

    @property
    def name(self) -> str:
        """The name of the command.

        Returns:
            str
                The name of the command.
        """
        return self._name

    @property
    def callback(self) -> typing.Callable[..., typing.Any]:
        """The callback function registered to the command.

        Returns:
            typing.Callable[... typing.Any]
                The callback function registered to the command.
        """
        return self._callback
