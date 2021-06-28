import nox


@nox.session(python=["3.8", "3.9", "3.10"])
def tests(session):
    session.run("poetry", "shell")
    session.run("poetry", "install")
    session.run("pytest")


@nox.session(python=["3.8", "3.9", "3.10"])
def lint(session):
    session.run("poetry", "shell")
    session.run("poetry", "install")
    session.run("pytest")
