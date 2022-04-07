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

import functools
from typing import Callable
from pathlib import Path

import nox
import toml

DictT = dict[str, str]
SessionT = Callable[[nox.Session], None]
InjectorT = Callable[[SessionT], SessionT]

with open("pyproject.toml") as f:
    data = toml.loads(f.read())["tool"]["poetry"]
    deps: DictT = {**data["dependencies"], **data["dev-dependencies"]}
    DEPS: DictT = {k.lower(): f"{k}{v}" for k, v in deps.items()}


def install(*packages: str) -> InjectorT:
    def inner(func: SessionT) -> SessionT:
        @functools.wraps(func)
        def wrapper(session: nox.Session) -> None:
            session.install("-U", *(DEPS[p] for p in packages))
            return func(session)

        return wrapper

    return inner


@nox.session(reuse_venv=True)
@install("pytest", "pytest-asyncio", "pytest-testdox", "mock", "hikari", "coverage")
def tests(session: nox.Session) -> None:
    session.run(
        "coverage",
        "run",
        "--omit",
        "tests/*",
        "-m",
        "pytest",
        "--testdox",
        "--log-level=INFO",
    )


@nox.session(reuse_venv=True)
@install("coverage")
def coverage(session: nox.Session) -> None:
    if not Path(".coverage").exists():
        session.skip("Skipping coverage")

    session.run("coverage", "report", "-m")


@nox.session(reuse_venv=True)
@install("pyright", "mypy", "hikari")
def types(session: nox.Session) -> None:
    session.run("mypy", "yami")
    session.run("pyright")


@nox.session(reuse_venv=True)
@install("black", "len8")
def formatting(session: nox.Session) -> None:
    session.run("black", ".", "--check")
    session.run("len8")


@nox.session(reuse_venv=True)
@install("flake8", "isort")
def imports(session: nox.Session) -> None:
    session.run("isort", "yami", "tests", "-cq")
    session.run(
        "flake8",
        "yami",
        "tests",
        "--select",
        "F4",
        "--extend-ignore",
        "E,F",
        "--extend-exclude",
        "__init__.py,",
    )


@nox.session(reuse_venv=True)
def licensing(session: nox.Session) -> None:
    missing: list[Path] = []
    files: list[Path] = [
        *Path("./yami").rglob("*.py"),
        *Path("./tests").glob("*.py"),
        *Path(".").glob("*.py"),
    ]

    for path in files:
        with open(path) as f:
            desc = f.readline()
            copy = f.readline()

            if "# Yami -" not in desc or "# Copyright (C)" not in copy:
                missing.append(path)

    if missing:
        session.error(
            "\nThe following files are missing their license:\n"
            + "\n".join(f" - {m}" for m in missing)
        )


@nox.session(reuse_venv=True)
@install("sphinx", "sphinx-rtd-theme", "sphinx-rtd-dark-mode", "hikari")
def docs(session: nox.Session) -> None:
    session.run(
        "python", "-m", "sphinx.cmd.build", "-b", "html", "-a", "./docs/source", "./docs/build"
    )
