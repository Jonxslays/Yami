from yami import __version__, Bot

import pytest


def test_version():
    assert __version__ == '0.1.1'

def test_bot():
    bot = Bot(
        token="1234",
        prefix="x",
        case_insensitive=False,
        shun_bots=False
    )
    assert bot.prefix == "x"
    assert bot._token == "1234"
    assert bot._case_insensitive == False
    assert bot._shun_bots == False
