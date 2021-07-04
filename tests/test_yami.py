import pytest  # type: ignore

from yami import Bot, __version__


def test_version() -> None:
    assert __version__ == "0.1.3"


def test_bot() -> None:
    bot = Bot(token="1234", prefix="x", case_insensitive=False, shun_bots=False, owners=[123, 654])
    assert bot.prefix == "x"
    assert bot._token == "1234"
    assert bot.case_insensitive == False
    assert bot.shun_bots == False
    assert 123 and 654 in bot.owners
