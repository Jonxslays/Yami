import typing as t

__all__: t.List[str] = [
    "YamiError", "CommandAlreadyRegistered"
]


class YamiError(Exception):
    pass


class CommandAlreadyRegistered(YamiError):
    pass
