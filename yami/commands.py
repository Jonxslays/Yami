import abc
import typing

__all__: typing.List[str] = [
    "AbstractCommand",
    "LegacyCommand",
]


class AbstractCommand(type, abc.ABC):
    """The base class all Yami Commands will inherit from.

    Args:

    """

    __slots__: typing.Sequence[str] = ()

    @property
    @abc.abstractproperty
    def callback(self) -> typing.Callable[..., typing.Any]:
        """The callback function registered to the command.

        Returns:
            typing.Callable[... typing.Any]
                The callback function registered to the command.
        """
        ...

    @property
    @abc.abstractproperty
    def name(self) -> str:
        """The name of the command.

        Returns:
            str
                The name of the command.
        """
        ...


class LegacyCommand(metaclass=AbstractCommand):
    """An object that represents a legacy message content command.

    Args:
        callback:
    """

    __slots__: typing.Sequence[str] = [
        "_callback",
        "_name",
    ]

    def __init__(
        self,
        callback: typing.Callable[..., typing.Any],
        name: str,
    ) -> None:
        self._callback = callback
        self._name = name

    @classmethod
    def new(cls, command: typing.Callable[..., typing.Any], name: str) -> "LegacyCommand":
        return cls(
            command,
            name=name,
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def callback(self) -> typing.Callable[..., typing.Any]:
        return self._callback
