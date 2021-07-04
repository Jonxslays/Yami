import typing as t

__all__: t.List[str] = [
    "YamiError", "CommandAlreadyRegistered", "ChannelNotFound"
]


class YamiError(Exception):
    pass


class CommandAlreadyRegistered(YamiError):
    pass


class ChannelNotFound(YamiError):
    pass
