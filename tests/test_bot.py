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
        case_insensitive=False,
        banner=None,
    )


@pytest.fixture()
def no_content_m_create_event() -> hikari.MessageCreateEvent:
    e = mock.Mock(spec=hikari.MessageCreateEvent)
    e.message = mock.Mock(spec=hikari.Message)
    e.message.content = hikari.UNDEFINED
    return e


@pytest.fixture()
def with_content_with_cmd_m_create_event() -> hikari.MessageCreateEvent:
    e = mock.Mock(spec=hikari.MessageCreateEvent)
    e.message = mock.Mock(spec=hikari.Message)
    e.message.content = "&&echo"
    return e


@pytest.fixture()
def with_content_no_cmd_m_create_event() -> hikari.MessageCreateEvent:
    e = mock.Mock(spec=hikari.MessageCreateEvent)
    e.message = mock.Mock(spec=hikari.Message)
    e.message.content = "FAKE"
    return e


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
    with pytest.raises(yami.BadArgument):
        model.add_command(mock.AsyncMock(), name="yoink", aliases="wrong")


def test_dup_aliases_add_command(model: yami.Bot) -> None:
    model.add_command(mock.AsyncMock(), name="moon", aliases=["ET"])
    with pytest.raises(yami.DuplicateCommand) as e:
        model.add_command(mock.AsyncMock(), name="sdf", aliases=["ET"])
        assert "alias 'ET' already in use" in e


def test_dup_name_add_command(model: yami.Bot) -> None:
    model.add_command(mock.AsyncMock(), name="giraffe")
    with pytest.raises(yami.DuplicateCommand) as e:
        model.add_command(mock.AsyncMock(), name="giraffe")
        assert "'giraffe' - name already in use" in e


def test_yield_commands(model: yami.Bot) -> None:
    for i in range(5):
        model.add_command(mock.AsyncMock(), name=f"cmd{i}")

    for i, cmd in enumerate(model.yield_commands()):
        assert isinstance(cmd, yami.MessageCommand)
        assert cmd.name.startswith(f"cmd{i}")

    gen = model.yield_commands()
    assert isinstance(gen, typing.Generator)

    assert next(gen).name == "cmd0"
    assert next(gen).name == "cmd1"
    assert next(gen).name == "cmd2"
    assert next(gen).name == "cmd3"
    assert next(gen).name == "cmd4"

    with pytest.raises(StopIteration):
        next(gen)


def test_sync_callback_fails(model: yami.Bot) -> None:
    with pytest.raises(yami.AsyncRequired):
        model.add_command(mock.Mock(), name="bad")


def test_get_command_with_alias_flag(model: yami.Bot) -> None:
    model.add_command(mock.AsyncMock(), name="hi", aliases=["bye"])
    cmd = model.get_command("bye", alias=True)

    assert isinstance(cmd, yami.MessageCommand)
    assert cmd.name == "hi"
    assert cmd.aliases == ["bye"]


@pytest.mark.asyncio()
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


@pytest.mark.asyncio()
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


@pytest.mark.asyncio()
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


@pytest.mark.asyncio()
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


@pytest.mark.asyncio()
async def test_bot__invoke_with_invalid_cmd(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    content_w_cmd_e = with_content_with_cmd_m_create_event
    model.add_command(mock.AsyncMock(), name="fake", aliases=["yup"])

    with pytest.raises(yami.CommandNotFound) as e:
        await model._invoke("&&", content_w_cmd_e, content_w_cmd_e.message.content)
        assert "No command found with name 'echo'" in e


@pytest.mark.asyncio()
async def test_bot__invoke_with_no_aliases(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    content_w_cmd_e = with_content_with_cmd_m_create_event
    model.add_command(mock.AsyncMock(), name="echo")

    result = await model._invoke("&&", content_w_cmd_e, content_w_cmd_e.message.content)
    assert result is None


@pytest.mark.asyncio()
async def test_bot__invoke_with_aliases(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    content_w_cmd_e = with_content_with_cmd_m_create_event
    model.add_command(mock.AsyncMock(), name="say", aliases=["echo"])

    result = await model._invoke("&&", content_w_cmd_e, content_w_cmd_e.message.content)
    assert result is None


@pytest.mark.asyncio()
async def test_bot__invoke_with_args(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    @model.command("echo")
    async def my_cute_callback(ctx: yami.MessageContext, num: int) -> int:
        return num + 1

    content_w_cmd_e = with_content_with_cmd_m_create_event
    result = await model._invoke("&&", content_w_cmd_e, "&&echo 10")

    assert result is None
    assert await model.get_command("echo").callback(mock.Mock(), 10) == 11

    with pytest.raises(yami.BadArgument) as e:
        await model._invoke("&&", content_w_cmd_e, "&&echo sixty")
        assert "Invalid arg 'sixty'" in e


@pytest.mark.asyncio()
async def test_bot__invoke_with_bool_args(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    @model.command("change")
    async def my_cute_callback(ctx: yami.MessageContext, state: bool) -> int:
        return state

    content_w_cmd_e = with_content_with_cmd_m_create_event
    result = await model._invoke("&&", content_w_cmd_e, "&&change True")
    assert result is None

    result = await model._invoke("&&", content_w_cmd_e, "&&change False")
    assert result is None

    assert await model.get_command("change").callback(mock.Mock(), True) is True
    assert await model.get_command("change").callback(mock.Mock(), False) is False

    with pytest.raises(yami.BadArgument) as e:
        await model._invoke("&&", content_w_cmd_e, "&&change what")
        assert "Invalid arg 'what'" in e

    with pytest.raises(yami.BadArgument) as e:
        await model._invoke("&&", content_w_cmd_e, "&&change what")
        assert "Invalid arg 'what'" in e


@pytest.mark.asyncio()
async def test_bot__invoke_with_adv_args(
    model: yami.Bot, with_content_with_cmd_m_create_event: hikari.MessageCreateEvent
) -> None:
    @model.command("dictionary")
    async def this_func(ctx: yami.MessageContext, data: dict[str, str]) -> int:
        return data

    content_w_cmd_e = with_content_with_cmd_m_create_event
    result = await model._invoke("&&", content_w_cmd_e, "&&dictionary {'hi':'bye'}")
    assert result is None

    assert (
        await model.get_command("dictionary").callback(mock.Mock(), "{'hi':'bye'}")
        == "{'hi':'bye'}"
    )
