<h1 align="center">Yami</h1>
<p align="center">A command handler that complements Hikari. <3</p>
<p align="center">
<a href="https://github.com/Jonxslays/Yami/blob/master/LICENSE"><img height="20" alt="License" src="https://img.shields.io/pypi/l/yami?label=License"></a>
<a href="https://pypi.org/project/yami"><img height="20" alt="Stable version" src="https://img.shields.io/pypi/v/yami?label=Stable&logo=pypi"></a>
</p>
<p align="center">
<a href="https://pepy.tech/project/yami"><img height="20" alt="Downloads" src="https://static.pepy.tech/personalized-badge/yami?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads"></a>
<a href="https://python.org"><img height="20" alt="Python versions" src="https://img.shields.io/pypi/pyversions/yami?label=Python&logo=python"></a>
</p>
<p align="center">
<a href="https://github.com/Jonxslays/Yami"><img height="20" alt="Last Commit" src="https://img.shields.io/maintenance/yes/2021?label=Maintained"></a>
<a href="https://github.com/Jonxslays/Yami"><img height="20" alt="Last Commit" src="https://img.shields.io/github/last-commit/jonxslays/yami?label=Last%20Commit&logo=git"></a>

<p align="center">
<a href="https://github.com/Jonxslays/Yami/actions/workflows/ci.yml"><img height="20" alt="Last Commit" src="https://img.shields.io/github/workflow/status/Jonxslays/Yami/CI?label=Build&logo=github"></a>
<a href="https://codeclimate.com/github/Jonxslays/Yami"><img height="20" alt="Last Commit" src="https://img.shields.io/codeclimate/coverage/Jonxslays/Yami?label=Coverage&logo=Code%20Climate"></a>
</p>

---

## Disclaimer

Still in early development. Not ready for use. (As in don't download)

## Getting started with Yami

Stable release

```bash
pip install yami
```

Development

```bash
pip install git+https://github.com/Jonxslays/Yami.git
```

#### Creating a Bot

```py
from os import environ

import yami


bot = yami.Bot(environ["TOKEN"], prefix="$")


@bot.command("add", "Adds 2 numbers together")
async def add_cmd(ctx: yami.MessageContext, num1: int, num2: int) -> None:
    # Basic python types are converted using their type hints.
    # More types coming soon :tm:
    await ctx.respond(f"{num1} + {num2} = {num1 + num2}")


if __name__ == "__main__":
    bot.run()
```

## License

Yami is licensed under the [GPL V3](https://github.com/Jonxslays/Yami/blob/master/LICENSE) license.
