import hikari
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
    assert model._commands == {}
    assert model._aliases == {}
    assert isinstance(model, hikari.GatewayBot)


def test_add_legacy_command_object(model: yami.Bot) -> None:
    cmd = yami.LegacyCommand(lambda: "Howdy", name="owo-cmd")
    model.add_command(cmd)
    assert model._commands == {"owo-cmd": cmd}
    assert cmd.callback() == "Howdy"
    assert cmd.name == "owo-cmd"
