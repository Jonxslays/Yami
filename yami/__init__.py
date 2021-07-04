"""
A command handler API wrapper for Hikari.
To get started you will want to initialize and instance of yami.Bot.
"""

from .commands import *
from .errors import *
from .modules import *
from .bot import *
from .context import *


with open("pyproject.toml", "r") as f:
    __version__ = f.readlines()[2].split(" ")[-1].strip('"\n')

__all__ = [
    "Bot", "Command", "YamiError", "Module", "command", "CommandAlreadyRegistered", "Context",
    "ChannelNotFound"
]
