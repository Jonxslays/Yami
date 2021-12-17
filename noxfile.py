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
    session.install("-U", DEPS["pytest"], DEPS["pytest-asyncio"], DEPS["mock"], DEPS["hikari"])
    session.run("pytest", "--verbose")


@nox.session(reuse_venv=True)
def types(session: nox.Session) -> None:
    session.install("-U", DEPS["pyright"], DEPS["mypy"], DEPS["hikari"])
    session.run("mypy", "yami")
    session.run("pyright")


@nox.session(reuse_venv=True)
def formatting(session: nox.Session) -> None:
    session.install("-U", DEPS["flake8"], DEPS["isort"], DEPS["black"], DEPS["len8"])

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

    session.run("isort", "yami", "tests", "-cq")
    session.run("black", ".", "--check")
    session.run("len8")
