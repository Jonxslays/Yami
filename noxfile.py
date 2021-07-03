import nox


@nox.session(reuse_venv=True)
def tests(session: nox.Session) -> None:
    session.run("poetry", "shell")
    session.run("poetry", "install")
    session.run("pytest", "--verbose")


@nox.session(reuse_venv=True)
def lint(session: nox.Session) -> None:
    session.run("poetry", "shell")
    session.run("poetry", "install")
    session.run("mypy", "--strict", ".")
