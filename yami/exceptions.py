class YamiException(Exception):
    """Base exception all Yami exceptions inherit from."""

    ...


class CommandNotFound(YamiException):
    """Raised when a command is invoked with a valid prefix, but no
    command with that name is found.
    """

    ...


class SyncCommand(YamiException):
    """Raised when a synchronous command is added to the bot via the
    yami.legacy decorator."""

    ...


class BadAlias(YamiException):
    """Raised what a bad argument is passed as aliases to a legacy
    command.
    """

    ...
