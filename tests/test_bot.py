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
async def test_add_legacy_command_object(model: yami.Bot) -> None:
    async_callback = mock.AsyncMock(return_value="Howdy")
    cmd = yami.LegacyCommand(async_callback, name="owo-cmd")
    model.add_command(cmd)

    assert model.commands == {"owo-cmd": cmd}
    assert await cmd.callback() == "Howdy"
    async_callback.assert_awaited_once()
    assert cmd.name == "owo-cmd"


@pytest.mark.asyncio()
async def test_add_non_command_object(model: yami.Bot) -> None:
    async_callback = mock.AsyncMock(return_value="Hello")
    model.add_command(async_callback, name="owo-cmd", aliases=["testing"])
    assert "owo-cmd" in model.commands

    cmd = model.get_command("owo-cmd")
    assert await cmd.callback() == "Hello"
    async_callback.assert_awaited_once()
    assert cmd.aliases == ["testing"]


def test_add_command_aliases_failure(model: yami.Bot) -> None:
    with pytest.raises(yami.BadAlias):
        model.add_command(mock.AsyncMock(), name="yoink", aliases="wrong")


def test_sync_callback_fails(model: yami.Bot) -> None:
    with pytest.raises(yami.SyncCommand):
        model.add_command(mock.Mock(), name="bad")
