from __future__ import annotations

import asyncio
import typing

from yami import exceptions

__all__: typing.List[str] = [
    "MessageCommand",
    "command",
]


class MessageCommand:
    """An object that represents a message content command.

    Args:
        callback: Callable[..., Any]
            The callback to run when the command is invoked.
        name: str
            The name of the command.
        descriptions: str
            The commands description.
        aliases: Iterable[str]
            The aliases to use for the command.

    """

    __slots__: typing.Sequence[str] = (
        "_aliases",
        "_callback",
        "_name",
        "_description",
    )

    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        name: str,
        description: str = "",
        aliases: typing.Iterable[str] = [],
    ) -> None:
        self._aliases = aliases
        self._callback = callback
        self._description = description
        self._name = name

        if not asyncio.iscoroutinefunction(callback):
            raise exceptions.AsyncRequired(
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
    def description(self) -> str:
        """The commands description.

        Returns:
            str
                The description of the command.
        """
        return self._description

    @property
    def callback(self) -> typing.Callable[..., typing.Any]:
        """The callback function registered to the command.

        Returns:
            typing.Callable[... typing.Any]
                The callback function registered to the command.
        """
        return self._callback


def command(
    name: str | None = None,
    description: str = "",
    *,
    aliases: typing.Iterable[str] = [],
) -> typing.Callable[..., MessageCommand]:
    """Decorator to add commands to the bot inside of modules."""
    return lambda callback: MessageCommand(
        callback,
        name if name else callback.__name__,
        description,
        aliases,
    )
