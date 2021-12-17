"""A command handler that complements Hikari."""

from __future__ import annotations

__all__: list[str] = [
    "Bot",
    "MessageContext",
    "MessageCommand",
    "YamiException",
    "CommandNotFound",
    "AsyncRequired",
    "command",
    "BadAlias",
]

__version__ = "0.2.4"
__author__ = "Jonxslays"
__description__ = "A command handler that complements Hikari."
__url__ = "https://github.com/Jonxslays/Yami"
__repository__ = __url__
__license__ = "GPL-3.0-only"

from yami.bot import *
from yami.commands import *
from yami.context import *
from yami.exceptions import *
from yami.modules import *
