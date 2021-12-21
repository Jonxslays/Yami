# Yami - A command handler that complements Hikari.
# Copyright (C) 2021 Jonxslays
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""A command handler that complements Hikari."""

from __future__ import annotations

__all__ = [
    "Bot",
    "MessageContext",
    "MessageCommand",
    "YamiException",
    "CommandNotFound",
    "command",
    "BadArgument",
    "DuplicateCommand",
    "Module",
    "utils",
    "ModuleException",
    "ModuleRemoveException",
    "ModuleAddException",
    "command",
    "ModuleLoadException",
    "ModuleUnloadException",
    "CheckException",
    "is_owner",
    "CheckRemovalFailed",
    "BadCheck",
    "CheckFailed",
    "CheckAddFailed",
    "is_in_guild",
    "is_in_dm",
    "has_role",
    "has_any_role",
    "has_perms",
    "custom_check",
    "is_the_cutest",
    "ListenerException",
    "Shared",
    "SharedNone",
    "YamiNoneType",
]

__version__ = "0.3.0"
__author__ = "Jonxslays"
__description__ = "A command handler that complements Hikari."
__url__ = "https://github.com/Jonxslays/Yami"
__repository__ = __url__
__license__ = "GPL-3.0-only"

from yami.bot import *
from yami.checks import *
from yami.commands import *
from yami.context import *
from yami.events import *
from yami.exceptions import *
from yami.modules import *
from yami.utils import *

from . import utils
