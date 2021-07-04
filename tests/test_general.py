import pytest  # type: ignore

from yami import __version__


def test_version() -> None:
    assert __version__ == "0.1.4"
