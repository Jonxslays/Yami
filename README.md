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
<a href="https://github.com/Jonxslays/Yami"><img height="20" alt="Last Commit" src="https://img.shields.io/maintenance/yes/2022?label=Maintained"></a>
<a href="https://github.com/Jonxslays/Yami"><img height="20" alt="Last Commit" src="https://img.shields.io/github/last-commit/jonxslays/yami?label=Last%20Commit&logo=git"></a>

<p align="center">
<a href="https://github.com/Jonxslays/Yami/actions/workflows/ci.yml"><img height="20" alt="Last Commit" src="https://img.shields.io/github/workflow/status/Jonxslays/Yami/CI?label=Build&logo=github"></a>
<a href="https://codeclimate.com/github/Jonxslays/Yami"><img height="20" alt="Last Commit" src="https://img.shields.io/codeclimate/coverage/Jonxslays/Yami?label=Coverage&logo=Code%20Climate"></a>
</p>

---

## Disclaimer

Still in early development. See the [TODO list](#TODO).

## Documentation

- [Stable](https://jonxslays.github.io/Yami)
- [Development](https://jonxslays.github.io/Yami/master)

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
import asyncio
import datetime
import functools
import os
import typing

import hikari
import yami

bot = yami.Bot(os.environ["TOKEN"], prefix="$")


# Can only be run in guilds.
@yami.is_in_guild()
@bot.command("add", "Adds 2 numbers", aliases=["sum"])
async def add_cmd(ctx: yami.MessageContext, num1: int, num2: int) -> None:
    # Basic builtin python types are converted for you using their type
    # hints (int, float, bool, complex, bytes). More types coming soon™.
    await ctx.respond(f"The sum is {num1 + num2}")


# Can only be run by members with one of these roles.
@yami.has_any_role("Admin", "Fibonacci")
@bot.command("fibonacci", aliases=("fib",))
async def fibonacci(ctx: yami.MessageContext, num: int) -> None:
    """Calculates the num'th term in the fibonacci sequence."""
    calc: typing.Callable[[int], int] = functools.lru_cache(
        lambda n: n if n < 2 else calc(n - 1) + calc(n - 2)
    )

    # Though we cache the function call, let's simulate thinking.
    async with ctx.trigger_typing():
        await asyncio.sleep(0.75)

    # Make a pretty embed.
    await ctx.respond(
        hikari.Embed(
            title=f"Fibonacci calculator",
            description=f"```{calc(num)}```",
            color=hikari.Color(0x8AFF8A),
            timestamp=datetime.datetime.now(tz=datetime.timezone.utc),
        )
        .set_footer(f"Term {num}")
        .set_author(
            name=(author := ctx.author).username,
            icon=author.avatar_url or author.default_avatar_url,
        )
    )


if __name__ == "__main__":
    bot.run()
```

## TODO

<div class="todolist" after=>
<div class="todocolumn">

<details>
<summary> :heavy_check_mark: Complete</summary>

- [x] CI
- [x] Testing (WIP)
- [x] Fully typed
- [x] Bot
- [x] Message Commands
- [x] Message Subcommands
- [x] Message Context
- [x] Modules
- [x] Exceptions (WIP)
- [x] Checks (WIP)
- [x] Basic arg parsing (builtin types)
- [x] Docs
- [x] Events (Mostly)

</details>
</div>

<div class="todocolumn">

<details>
<summary> :x: Incomplete</summary>

- [ ] Module listeners
- [ ] Hooks?
- [ ] Slash Commands
- [ ] Slash Context
- [ ] Converters (WIP)
- [ ] Utils (WIP)
- [ ] Full blown arg parsing (hikari types)
- [ ] QOL methods (WIP)
- [ ] Logging (WIP)

</details>
</div>
</div>

---

## Contributing

Yami is open to contributions. To get started check out the
[contributing guide](https://github.com/Jonxslays/Yami/blob/master/CONTRIBUTING.md).

## License

Yami is licensed under the [GPLV3](https://github.com/Jonxslays/Yami/blob/master/LICENSE) license.
