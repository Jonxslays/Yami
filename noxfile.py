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

from pathlib import Path

import nox
import toml


def get_dependencies() -> dict[str, str]:
    with open("pyproject.toml") as f:
        data = toml.loads(f.read())["tool"]["poetry"]
        deps = data["dev-dependencies"]
        deps.update(data["dependencies"])

    return dict((k, f"{k}{v}") for k, v in deps.items())


DEPS = get_dependencies()


@nox.session(reuse_venv=True)
def tests(session: nox.Session) -> None:
    session.install(
        "-U",
        DEPS["pytest"],
        DEPS["pytest-asyncio"],
        DEPS["pytest-testdox"],
        DEPS["mock"],
        DEPS["hikari"],
        DEPS["coverage"],
    )

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
def coverage(session: nox.Session) -> None:
    session.install("-U", DEPS["coverage"])

    if not Path(".coverage").exists():
        session.skip("Skipping coverage")

    session.run("coverage", "report", "-m")


@nox.session(reuse_venv=True)
def types(session: nox.Session) -> None:
    session.install("-U", DEPS["pyright"], DEPS["mypy"], DEPS["hikari"])
    session.run("mypy", "yami")
    session.run("pyright")


@nox.session(reuse_venv=True)
def formatting(session: nox.Session) -> None:
    session.install("-U", DEPS["black"], DEPS["len8"])
    session.run("black", ".", "--check")
    session.run("len8")


@nox.session(reuse_venv=True)
def imports(session: nox.Session) -> None:
    session.install("-U", DEPS["flake8"], DEPS["isort"])
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
