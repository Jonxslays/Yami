import pytest # type: ignore

import yami


@pytest.fixture() # type: ignore
def bot() -> yami.Bot:
    bot = yami.Bot(
        token="1234", prefix="x",
        case_insensitive=False, shun_bots=False,
        owners=[123, 654]
    )
    bot._commands["help"] = yami.Command(name="help")
    return bot


def test_bot_init(bot: yami.Bot) -> None:
    assert bot.prefix == "x"
    assert bot._token == "1234"
    assert bot.case_insensitive == False
    assert bot.shun_bots == False
    assert 123 and 654 in bot.owners


def test_bot_commands(bot: yami.Bot) -> None:
    assert len(bot.commands) == 1
    assert type(bot.commands.pop()) is yami.Command
    assert "help" in (c.name for c in bot.commands)
