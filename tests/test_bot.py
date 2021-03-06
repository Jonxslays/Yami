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

from __future__ import annotations

import typing

import hikari
import mock
import pytest

import yami


@pytest.fixture()
def model() -> yami.Bot:
    return yami.Bot(
        token="12345",
        prefix="&&",
        banner=None,
        raise_cmd_not_found=True,
    )


@pytest.fixture()
def no_content_m_create_event() -> hikari.MessageCreateEvent:
    e = mock.Mock()
    e.message = mock.Mock()
    e.message.content = hikari.UNDEFINED
    return e


@pytest.fixture()
def with_content_with_cmd_m_create_event() -> hikari.MessageCreateEvent:
    e = mock.Mock()
    e.message = mock.Mock()
    e.message.content = "&&echo"
    return e


@pytest.fixture()
def with_content_no_cmd_m_create_event() -> hikari.MessageCreateEvent:
    e = mock.Mock()
    e.message = mock.Mock()
    e.message.content = "FAKE"
    return e


def test_bot_instantiation(model: yami.Bot) -> None:
    assert model._prefix == ("&&",)
    assert model._token == "12345"
    assert model.commands == {}
    assert model.aliases == {}
    assert isinstance(model, hikari.GatewayBot)


async def test_add_message_command_object(model: yami.Bot) -> None:
    async_callback = mock.AsyncMock(return_value="Howdy")
    cmd = yami.MessageCommand(
        async_callback, name="owo-cmd", description="", aliases=(), raise_conversion=False
    )
    model.add_command(cmd)

    assert model.commands == {"owo-cmd": cmd}
    assert await cmd.callback() == "Howdy"
    assert cmd.name == "owo-cmd"
    assert cmd.raise_conversion is False
    async_callback.assert_awaited_once()


async def test_add_non_command_object(model: yami.Bot) -> None:
    async_callback = mock.AsyncMock(return_value="Hello")
    model.add_command(async_callback, name="owo-cmd", aliases=["testing"])
    assert "owo-cmd" in model.commands

    cmd = model.get_command("owo-cmd")
    assert cmd
    assert await cmd.callback() == "Hello"
    assert cmd.aliases == ["testing"]
    async_callback.assert_awaited_once()


def test_add_command_aliases_failure(model: yami.Bot) -> None:
    with pytest.raises(TypeError):
        model.add_command(mock.AsyncMock(), name="yoink", aliases="wrong")  # type: ignore


def test_dup_aliases_add_command(model: yami.Bot) -> None:
    model.add_command(mock.AsyncMock(), name="moon", aliases=["ET"])
    with pytest.raises(yami.DuplicateCommand) as e:
        model.add_command(mock.AsyncMock(), name="sdf", aliases=["ET"])
        assert "alias 'ET' already in use" in str(e)


def test_dup_name_add_command(model: yami.Bot) -> None:
    model.add_command(mock.AsyncMock(), name="giraffe")
    with pytest.raises(yami.DuplicateCommand) as e:
        model.add_command(mock.AsyncMock(), name="giraffe")
        assert "'giraffe' - name already in use" in str(e)


def test_iter_commands(model: yami.Bot) -> None:
    for i in range(5):
        model.add_command(mock.AsyncMock(), name=f"cmd{i}")

    for i, cmd in enumerate(model.iter_commands()):
        assert isinstance(cmd, yami.MessageCommand)
        assert cmd.name.startswith(f"cmd{i}")

    gen = model.iter_commands()
    assert isinstance(gen, typing.Generator)

    assert next(gen).name == "cmd0"
    assert next(gen).name == "cmd1"
    assert next(gen).name == "cmd2"
    assert next(gen).name == "cmd3"
    assert next(gen).name == "cmd4"

    with pytest.raises(StopIteration):
        next(gen)


def test_get_command(model: yami.Bot) -> None:
    model.add_command(mock.AsyncMock(), name="hi", aliases=["bye"])
    cmd = model.get_command("bye")

    assert isinstance(cmd, yami.MessageCommand)
    assert cmd.name == "hi"
    assert cmd.aliases == ["bye"]


async def test_bot_command_deco(model: yami.Bot) -> None:
    ctx = mock.Mock()

    @model.command("tester", "To be or not to be...", aliases=["lol"])
    async def tester_callback(ctx: yami.MessageContext) -> int:
        return 369

    cmd = model.get_command("tester")

    assert cmd is not None
    assert len(model.commands) == 1
    assert cmd.name == "tester"
    assert cmd.description == "To be or not to be..."
    assert cmd.aliases == ["lol"]
    assert await cmd.callback(ctx) == 369


async def test_bot__listen_no_content(
    model: yami.Bot, no_content_m_create_event: hikari.MessageCreateEvent
) -> None:
    no_content_e = no_content_m_create_event
    with mock.patch.object(yami.Bot, "_invoke") as _invoke:
        _invoke.return_value = 100
        result = await model._listen(no_content_e)

        _invoke.assert_not_called()
        _invoke.assert_not_awaited()
        assert result is None


async def test_bot__listen_with_content_no_cmd(
    model: yami.Bot, with_content_no_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    content_no_cmd_e = with_content_no_cmd_m_create_event
    with mock.patch.object(yami.Bot, "_invoke") as _invoke:
        _invoke.return_value = 100
        model.add_command(mock.AsyncMock(), name="echo", aliases=["yup"])
        result = await model._listen(content_no_cmd_e)

        _invoke.assert_not_called()
        _invoke.assert_not_awaited()
        assert result is None


async def test_bot__listen_with_content_with_cmd(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    content_w_cmd_e = with_content_with_cmd_m_create_event
    with mock.patch.object(yami.Bot, "_invoke") as _invoke:
        _invoke.return_value = 100
        model.add_command(mock.AsyncMock(), name="echo", aliases=["yup"])
        result = await model._listen(content_w_cmd_e)

        _invoke.assert_called_once_with("&&", content_w_cmd_e, "&&echo")
        _invoke.assert_awaited_once()
        assert result == 100


async def test_bot__invoke_with_invalid_cmd(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    content_w_cmd_e = with_content_with_cmd_m_create_event
    model.add_command(mock.AsyncMock(), name="fake", aliases=["yup"])

    with pytest.raises(yami.CommandNotFound) as e:
        await model._invoke("&&", content_w_cmd_e, content_w_cmd_e.message.content)  # type: ignore

    assert "No command found with name 'echo'" in str(e.value)
