# Yami - A command handler that complements Hikari.
# Copyright (C) 2021-present Jonxslays
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
"""Provides cli functionality for versioning info."""

from __future__ import annotations

import platform
from pathlib import Path

from yami import __git_sha__, __version__


def info() -> None:
    """Prints package/system info and exits."""
    path = Path(__file__).parent.absolute()
    py_impl = platform.python_implementation()
    py_ver = platform.python_version()
    py_c = platform.python_compiler()
    p = platform.uname()

    print(f"Yami v{__version__} {__git_sha__}")
    print(f"@ {path}")
    print(f"{py_impl} {py_ver} {py_c}")
    print(f"{p.system} {p.node} {p.release} {p.machine}")
    print(p.version)
