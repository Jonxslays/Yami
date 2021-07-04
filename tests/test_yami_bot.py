import pytest # type: ignore

import yami


@pytest.fixture() # type: ignore
def bot() -> yami.Bot:
    bot = yami.Bot(
        token="1234", prefix="x",
        case_insensitive=False, shun_bots=False,
        owners=[123, 654]
    )
    bot._commands["help"] = yami.Command(lambda x: "123", name="help")
    bot._modules["test-mod"] = yami.Module(name="test-mod")
    return bot


def test_bot_init(bot: yami.Bot) -> None:
    assert bot.prefix is "x"
    assert bot._token is "1234"
    assert not bot.case_insensitive
    assert not bot.shun_bots
    assert 123 and 654 in bot.owners


def test_bot_commands(bot: yami.Bot) -> None:
    assert len(bot.commands) == 1
    assert type(bot.commands.pop()) is yami.Command
    assert "help" in (c.name for c in bot.commands)


def test_bot_modules(bot: yami.Bot) -> None:
    assert len(bot.modules) == 1
    assert type(bot.modules.pop()) is yami.Module
    assert "test-mod" in (m.name for m in bot.modules)


def test_add_command(bot: yami.Bot) -> None:

    @bot.command(name="test", aliases=["testing"])
    def test_cmd() -> None:
        pass

    assert len(bot.commands) == 2
    assert "test" in (c.name for c in bot.commands)
    assert "testing" in bot.aliases
    assert test_cmd in bot.commands


def test_get_hidden_command(bot: yami.Bot) -> None:

    @bot.command(name="secret", hidden=True)
    def test_cmd() -> None:
        pass

    secret_cmd = bot.get_command("secret")

    assert type(secret_cmd) is yami.Command


def test_get_command(bot: yami.Bot) -> None:
    help_cmd = bot.get_command("help")

    assert type(help_cmd) is yami.Command
    assert help_cmd.name is "help"
    assert help_cmd.aliases == []
    assert not help_cmd.hidden
