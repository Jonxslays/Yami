=======
Modules
=======

#################
What is a module?
#################

In Yami, a ``Module`` is any class that inherits from :obj:`~yami.Module`.
This is typically commands or functions that should be grouped together
for one reason or another. If you're coming from ``discord.py``, they
are Yami's equivalent to a ``Cog``.

###############
Create a module
###############

..  code-block:: python

    # fun.py
    import yami

    class Games(yami.Module):

        @yami.command("slap")
        async def slap_cmd(ctx: yami.MessageContext, user_id: int) -> None:
            """Slaps a user."""
            await ctx.respond(f"<@!{ctx.author.id}> slapped <@!{user_id}>")

    class ClassicWow(yami.Module):

        @yami.command("logs")
        async def logs_cmd(ctx: yami.MessageContext, name: str) -> None:
            """Fetches logs search link for a user."""
            await ctx.respond(f"https://classic.warcraftlogs.com/search/?term={name}")

The ideal implementation contains a directory with files that contain
:obj:`~yami.Module` subclasses. These files do not require any special
load or unload functions, Yami takes care of that for you.

..  warning::

    For any of the following methods that request the ``name`` of a
    module, the name is case sensitive and should match the class name.

#############
Load a module
#############

Loading a module will import the class and initialize it, passing a
:obj:`~yami.Bot` instance to its constructor.

..  code-block:: bash

    # Directory structure
    .
    ├── main.py
    └── modules
        ├── admin.py
        ├── fun.py
        └── meta.py

..  code-block:: python

    # main.py
    from os import environ

    import yami

    bot = yami.Bot(environ["TOKEN"], "$")
    bot.load_all_modules("./modules")

    if __name__ == "__main__":
        bot.run()


In the example above all the classes that subclass :obj:`yami.Module`
that are inside the files underneath the ``modules`` directory will be
loaded to the bot, and that means all their commands will be loaded too.

You can load modules individually from a file as well:

..  code-block:: python

    # main.py
    from os import environ

    import yami

    bot = yami.Bot(environ["TOKEN"], "$")
    bot.load_module("Games", "./modules/fun")

    # This is also valid.
    bot.load_module("ClassicWow", "./modules/fun.py")

    if __name__ == "__main__":
        bot.run()

###############
Unload a module
###############

Unloading a module will remove it's command from the bot, and place it
into an unloaded state but the module itself will still be attached to
the bot, in :obj:`yami.Bot.modules`. To remove the module completely see
`remove_module <modules#remove-a-module>`_

..  code-block:: python

    # main.py
    from os import environ

    import yami

    bot = yami.Bot(environ["TOKEN"], "$")
    bot.load_all_modules("./modules")

    @yami.is_owner()
    @bot.command("unload")
    async def unload_cmd(ctx: yami.MessageContext, mod: str) -> None:
        """Unloads a module."""
        if (fetched := ctx.bot.get_module(mod)) and fetched.is_loaded:
            ctx.bot.unload_module(fetched.name)
            await ctx.respond("Done!")
        else:
            await ctx.respond("Failed to unload the module.")

    if __name__ == "__main__":
        bot.run()

###############
Remove a module
###############

Removing a module will remove it completely from the bot, including all
commands.

..  code-block:: python

    # main.py
    from os import environ

    import yami

    bot = yami.Bot(environ["TOKEN"], "$")
    bot.load_all_modules("./modules")

    bot.remove_module("Games")

    if __name__ == "__main__":
        bot.run()
