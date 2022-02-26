===============
Getting started
===============

..  role:: ul
    :class: ul

############
Installation
############

If you are unfamiliar with ``pip``, the Python package manger you can read
more `here <https://pip.pypa.io/en/latest/getting-started/>`_.

**Stable release**

..  code-block:: bash

    pip install yami

    # Alternatively
    python -m pip install yami

**Development**

..  code-block:: bash

    pip install git+https://github.com/Jonxslays/Yami.git

    # Alternatively
    python -m pip install git+https://github.com/Jonxslays/Yami.git

########
Speedups
########

There are some optional speedups that can be installed.

These are well documented in the Hikari
`README <https://github.com/hikari-py/hikari>`_.

- `uvloop <https://pypi.org/project/uvloop/>`_:
  ``pip install uvloop``

  * A replacement for the asyncio event loop.
  * :ul:`Only available on UNIX-like operating systems`.

- `hikari[speedups] <https://github.com/hikari-py/hikari#hikarispeedups>`_:

  * Installs ``aiodns``, ``cchardet``, ``brotli``, and ``ciso8601``.
  * :ul:`Requires a working C compiler on the system`.

  Yami can be installed with speedups automatically as well using
  ``pip install "yami[speedups]"``

############
Create a Bot
############

Make sure you have a bot token, obtained from the `Discord
developer portal <https://discord.com/developers/applications>`_.

..  code-block:: python

    from os import environ

    import hikari
    import yami


    bot = yami.Bot(environ["TOKEN"], "$", allow_extra_args=True)

    @bot.listen(hikari.StartedEvent)
    async def on_started(_: hikari.StartedEvent) -> None:
        print(f"Bot is ready. Latency: {bot.heartbeat_latency}")


    if __name__ == "__main__":
        bot.run()
