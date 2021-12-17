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

from __future__ import annotations

import hikari
import mock
import pytest

import yami


@pytest.fixture()
def model() -> yami.Bot:
    return yami.Bot(
        token="12345",
        prefix="&&",
        case_insensitive=False,
        banner=None,
    )


def test_bot_instantiation(model: yami.Bot) -> None:
    assert model._prefix == ("&&",)
    assert model._token == "12345"
    assert not model._case_insensitive
    assert model.commands == {}
    assert model.aliases == {}
    assert isinstance(model, hikari.GatewayBot)


@pytest.mark.asyncio()
async def test_add_message_command_object(model: yami.Bot) -> None:
    async_callback = mock.AsyncMock(return_value="Howdy")
    cmd = yami.MessageCommand(async_callback, name="owo-cmd")
    model.add_command(cmd)

    assert model.commands == {"owo-cmd": cmd}
    assert await cmd.callback() == "Howdy"
    assert cmd.name == "owo-cmd"
    async_callback.assert_awaited_once()


@pytest.mark.asyncio()
async def test_add_non_command_object(model: yami.Bot) -> None:
    async_callback = mock.AsyncMock(return_value="Hello")
    model.add_command(async_callback, name="owo-cmd", aliases=["testing"])
    assert "owo-cmd" in model.commands

    cmd = model.get_command("owo-cmd")
    assert await cmd.callback() == "Hello"
    assert cmd.aliases == ["testing"]
    async_callback.assert_awaited_once()


def test_add_command_aliases_failure(model: yami.Bot) -> None:
    with pytest.raises(yami.BadAlias):
        model.add_command(mock.AsyncMock(), name="yoink", aliases="wrong")


def test_sync_callback_fails(model: yami.Bot) -> None:
    with pytest.raises(yami.AsyncRequired):
        model.add_command(mock.Mock(), name="bad")


def test_bot_command_deco(model: yami.Bot) -> None:
    @model.command("tester", "To be or not to be...", aliases=["lol"])
    async def tester_callback(ctx: yami.MessageContext, arg: int) -> None:
        await ctx.respond(f"arg was {arg}")

    cmd = model.get_command("tester")

    assert cmd is not None
    assert len(model.commands) == 1
    assert cmd.name == "tester"
    assert cmd.description == "To be or not to be..."
    assert cmd.aliases == ["lol"]
