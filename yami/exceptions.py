class YamiException(Exception):
    """Base exception all Yami exceptions inherit from."""

    ...


class CommandNotFound(YamiException):
    """Raised when a command is invoked with a valid prefix, but no
    command with that name is found.
    """

    ...
