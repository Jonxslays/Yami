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
def guild_ctx() -> yami.MessageContext:
    c = yami.MessageCommand(
        mock.AsyncMock(return_value=3),
        name="oi",
    )

    b = yami.Bot(
        token="12345",
        prefix="&&",
        case_insensitive=False,
        banner=None,
    )

    msg = mock.Mock(spec=hikari.Message)
    msg.author = "AUTHOR"
    msg.guild_id = 888
    msg.channel_id = 976969
    msg.id = 3258
    msg.content = "happy december folks"

    return yami.MessageContext(
        b,
        msg,
        c,
        "$$",
    )


@pytest.fixture()
def dm_ctx() -> yami.MessageContext:
    c = yami.MessageCommand(
        mock.AsyncMock(return_value=3),
        name="oi",
    )

    b = yami.Bot(
        token="12345",
        prefix="&&",
        case_insensitive=False,
        banner=None,
    )

    msg = mock.Mock(spec=hikari.Message)
    msg.author = "AUTHOR"
    msg.guild_id = None
    msg.channel_id = 976969
    msg.id = 3258
    msg.content = "happy january folks"

    return yami.MessageContext(
        b,
        msg,
        c,
        "$$",
    )


def test_message_context_init(guild_ctx: yami.MessageContext) -> None:
    assert guild_ctx.bot._token == "12345"
    assert guild_ctx.author == "AUTHOR"
    assert guild_ctx.prefix == "$$"
    assert guild_ctx.command.name == "oi"
    assert guild_ctx.guild_id == 888
    assert guild_ctx.channel_id == 976969
    assert guild_ctx.message_id == 3258
    assert guild_ctx.content == "happy december folks"
    assert guild_ctx.message.id == 3258


@pytest.mark.asyncio()
async def test_message_context_respond(guild_ctx: yami.MessageContext) -> None:
    with mock.patch.object(yami.MessageContext, "respond") as resp:
        await guild_ctx.respond("hello")
        resp.assert_called_once_with("hello")
        resp.assert_awaited_once()


@pytest.mark.asyncio()
async def test_getch_guild_in_guild(guild_ctx: yami.MessageContext) -> None:
    with mock.patch.object(hikari.GatewayBot, "cache") as cache_:
        cache_.get_guild = mock.Mock(return_value=888)

        r = await guild_ctx.getch_guild()
        cache_.get_guild.assert_called_once()
        assert r == 888


@pytest.mark.asyncio()
async def test_getch_guild_in_dm(dm_ctx: yami.MessageContext) -> None:
    r = await dm_ctx.getch_guild()
    assert r is None


@pytest.mark.asyncio()
async def test_getch_channel(guild_ctx: yami.MessageContext) -> None:
    with mock.patch.object(hikari.GatewayBot, "cache") as cache_:
        cache_.get_guild_channel = mock.Mock(return_value=888)

        r = await guild_ctx.getch_channel()
        cache_.get_guild_channel.assert_called_once()
        assert r == 888
