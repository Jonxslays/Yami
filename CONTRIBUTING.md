# Contributing

Thanks for your interest in Yami! Here are some tips for contributing.

## Guidelines

- Code should be [PEP 8](https://www.python.org/dev/peps/pep-0008/) compliant.
- Implementations should be well tested before opening a pull request
- If you have an idea, but are unsure on the proper implementation - open an issue.
- Use informative commit messages.
- Code should be written in [black](https://github.com/psf/black)'s code style.
- Max code line length of 99, max docs line length of 72.

Please see the [code of conduct](https://github.com/Jonxslays/Yami/blob/master/CODE_OF_CONDUCT.md)
for additional guidelines.

## Installing poetry

Yami uses [Poetry](https://python-poetry.org/) for dependency management. The following commands
could be changed in the future.

Check out poetry's full [installation guide](https://python-poetry.org/docs/master/#installation)
for detailed instructions.

- Macosx/Linux

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

- Windows

```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

- Verify installation

```bash
poetry --version
```

## Managing dependencies

1) Create a fork of Yami, and clone the fork to your local machine.
2) Change directory into the project dir `Yami`.
3) Run `poetry shell` to create a new virtual env, and activate it.
4) Run `poetry install` to install dependencies (this includes dev deps).

While this should not be the case, if there are any dependency changes please
detail them in your pull request.

Dependencies can be added and removed from the project with poetry.

```bash
poetry add aiohttp
poetry add mypy --dev

poetry remove aiohttp
poetry remove mypy --dev
```

## Writing code
- Check out a new branch to commit your work to, e.g. `git checkout -b bugfix/typing-errors`.
- Make your changes, and commit your work.
- Run `nox` and address any issues that arise.
- Open a pull request into the master branch of this repository.

After submitting your PR, it will be reviewed (and hopefully merged!). Thanks again for taking the
time to read this contributing guide, and for your interest in Yami. I look forward to working with
you.
