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


class TestMessageContext:
    @pytest.fixture()
    def message(self) -> hikari.Message:
        return mock.AsyncMock()

    @pytest.fixture()
    def message_context(self, message: hikari.Message) -> yami.MessageContext:
        return yami.MessageContext(mock.Mock(), message, mock.Mock(), "$$")

    def test_init(self) -> None:
        bot = object()
        message = object()
        command = object()
        prefix = "@@"

        ctx = yami.MessageContext(bot, message, command, prefix)

        assert ctx.bot == bot
        assert ctx.message == message
        assert ctx.command == command
        assert ctx.prefix == prefix

    def test_properties(self, message_context: yami.MessageContext, message: mock.Mock) -> None:
        message.author = "AUTHOR"
        message.guild_id = 888
        message.channel_id = 976969
        message.id = 3258
        message.content = "happy december folks"

        assert message_context.author == "AUTHOR"
        assert message_context.prefix == "$$"
        assert message_context.guild_id == 888
        assert message_context.channel_id == 976969
        assert message_context.message_id == 3258
        assert message_context.content == "happy december folks"
        assert message_context.message is message

    @pytest.mark.asyncio()
    async def test_message_context_respond(self, message_context: yami.MessageContext) -> None:
        await message_context.respond("hello", kwarg="testing")
        message_context._message.respond.assert_awaited_once_with("hello", kwarg="testing")

    @pytest.mark.asyncio()
    async def test_getch_guild_with_cache(self, message_context: yami.MessageContext) -> None:
        message_context._message.guild_id = 888
        message_context._bot.rest.fetch_guild = mock.AsyncMock()
        message_context._bot.cache.get_guild = mock.Mock()

        assert (
            await message_context.getch_guild()
            is message_context._bot.cache.get_guild.return_value
        )

        message_context._bot.cache.get_guild.assert_called_once_with(888)
        message_context._bot.rest.fetch_guild.assert_not_called()

    @pytest.mark.asyncio()
    async def test_getch_guild_no_cache(self, message_context: yami.MessageContext) -> None:
        message_context._message.guild_id = 888
        message_context._bot.rest.fetch_guild = mock.AsyncMock()
        message_context._bot.cache.get_guild = mock.Mock(return_value=None)

        assert (
            await message_context.getch_guild()
            is message_context._bot.rest.fetch_guild.return_value
        )

        message_context._bot.cache.get_guild.assert_called_once_with(888)
        message_context._bot.rest.fetch_guild.assert_awaited_once_with(888)

    @pytest.mark.asyncio()
    async def test_getch_guild_when_in_dm(self, message_context: yami.MessageContext) -> None:
        message_context._message.guild_id = None
        message_context._bot.rest.fetch_guild = mock.AsyncMock()
        message_context._bot.cache.get_guild = mock.Mock()

        assert await message_context.getch_guild() is None

        message_context._bot.cache.get_guild.assert_not_called()
        message_context._bot.rest.fetch_guild.assert_not_called()

    @pytest.mark.asyncio()
    async def test_getch_channel_with_cache(self, message_context: yami.MessageContext) -> None:
        channel = object()
        message_context._message.channel_id = 42
        message_context._bot.rest.fetch_channel = mock.AsyncMock()
        message_context._bot.cache.get_guild_channel = mock.Mock(return_value=channel)

        assert await message_context.getch_channel() is channel

        message_context._bot.cache.get_guild_channel.assert_called_once_with(42)
        message_context._bot.rest.fetch_channel.assert_not_called()

    @pytest.mark.asyncio()
    async def test_getch_channel_no_cache(self, message_context: yami.MessageContext) -> None:
        channel = object()
        message_context._message.channel_id = 69
        message_context._bot.rest.fetch_channel = mock.AsyncMock(return_value=channel)
        message_context._bot.cache.get_guild_channel = mock.Mock(return_value=None)

        assert await message_context.getch_channel() is channel

        message_context._bot.cache.get_guild_channel.assert_called_once_with(69)
        message_context._bot.rest.fetch_channel.assert_awaited_once_with(69)
