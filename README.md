<h1 align="center">Yami</h1>
<p align="center">A command handler that complements Hikari. <3</p>
<p align="center">
<a href="https://pepy.tech/project/yami"><img height="20" alt="Downloads" src="https://static.pepy.tech/personalized-badge/yami?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads"></a>
<a href="https://python.org"><img height="20" alt="Python versions" src="https://img.shields.io/pypi/pyversions/yami?label=Python&logo=python"></a>
</p>
<p align="center">
<a href="https://github.com/Jonxslays/Yami/blob/master/LICENSE"><img height="20" alt="License" src="https://img.shields.io/pypi/l/yami?label=License"></a>
<a href="https://pypi.org/project/yami"><img height="20" alt="Stable version" src="https://img.shields.io/pypi/v/yami?label=Stable&logo=pypi"></a>
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

Still in early development. See the [TODO list](#TODO).

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

from yami import Bot, MessageContext


bot = Bot(environ["TOKEN"], prefix="$")


@bot.command("add", "Add 2 numbers together, and squares them maybe", aliases=["sum"])
async def add_cmd(ctx: MessageContext, num1: int, num2: int, square: bool = False) -> None:
    # Basic builtin python types are converted for you using their type
    # hints (int, float, bool). More advanced conversions like
    # dict[str, str] are not supported and the argument will be passed
    # as a string. More types coming soon™.
    num = num1 + num2
    await ctx.respond(f"The result is {num ** 2 if square else num}")


if __name__ == "__main__":
    bot.run()
```

## TODO

<div class="todolist" after=>
<div class="todocolumn">

<details>
<summary> :heavy_check_mark: Complete</summary>

- [x] CI and testing
- [x] Fully typed
- [x] Bot
- [x] Message Commands
- [x] Message Context
- [x] Modules
- [x] Exceptions (WIP)

</details>
</div>

<div class="todocolumn">

<details>
<summary> :x: Incomplete</summary>

- [ ] Checks
- [ ] Events
- [ ] Hooks?
- [ ] Slash Commands
- [ ] Slash Context
- [ ] Converters
- [ ] Utils
- [ ] Proper command arg type parsing
- [ ] QOL methods
- [ ] Logging

</details>
</div>
</div>

---

## Contributing

Yami is open to contributions. To get started check out the
[contributing guide](https://github.com/Jonxslays/Yami/blob/master/CONTRIBUTING.md).

## License

Yami is licensed under the [GPL V3](https://github.com/Jonxslays/Yami/blob/master/LICENSE) license.
