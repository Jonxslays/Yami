from .commands import *
from .errors import *
from .bot import Bot

with open("pyproject.toml", "r") as f:
    __version__ = f.readlines()[2].split(" ")[-1].strip('"\n')

__all__ = ["Bot", "Command", "YamiError"]
