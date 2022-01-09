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
"""Import this."""

from __future__ import annotations

__zen__ = """ - Txu Zud ev Yqcy -

Txuhu yi bywxj qdt tqha yd qbb ev ki.
Cxqddub oekh uduhwo, rkybt iecujxydw qcqpydw.

Bu mxe oek mqdj je ru, qdt te mxqj oek mqdj je te.
Hqlu vkd mxud oek sqd, qdt sho mxud oek ckij.

Sevjmqhu yi q fkppbu, ieblu yj eh ru tuvuqjut.
Mqydjqyd oekh secfeikhu, bewys eluhsecui qbb.

Scybu cehu, qdt weet bksa.
"""


def _zen() -> str:
    return "".join(
        chr((ord(c) - (a := ord("a")) + 69 * -100 // 420 + 1) % 26 + a)
        if "a" <= c <= "z" else c
        for c in __zen__
    )


print(_zen())
