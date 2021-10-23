from __future__ import annotations

import asyncio
import typing

from yami import exceptions

__all__: typing.List[str] = [
    "LegacyCommand",
    "legacy",
]


class LegacyCommand:
    """An object that represents a legacy message content command.

    Args:
        callback:
    """

    __slots__: typing.Sequence[str] = (
        "_aliases",
        "_callback",
        "_name",
    )

    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        name: str,
        aliases: typing.Iterable[str] = [],
    ) -> None:
        self._aliases = aliases
        self._callback = callback
        self._name = name

        if not asyncio.iscoroutinefunction(callback):
            raise exceptions.SyncCommand(
                f"Command callbacks must be asynchronous: function {callback}"
            )

    @property
    def aliases(self) -> typing.Iterable[str]:
        """The aliases for the command.

        Returns:
            Iterable[str]
                The aliases for the command or an empty list if there
                are none.
        """
        return self._aliases

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


def legacy(
    *,
    name: str | None = None,
    aliases: typing.Iterable[str] = [],
) -> typing.Callable[..., LegacyCommand]:
    """Decorator to add commands to the bot inside of modules."""
    return lambda callback: LegacyCommand(callback, name if name else callback.__name__, aliases)
