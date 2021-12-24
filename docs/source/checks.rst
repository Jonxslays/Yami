======
Checks
======

..  role:: ul
    :class: ul

:obj:`~yami.Check` objects allow you to control the context in which
your command can be invoked. A lot of useful ones are built into the
library, but you can make your own custom checks as well.

..  warning::

    - :obj:`~yami.Check` decorators :ul:`must` be placed :ul:`above`
      the ``command`` decorator.

###############
Built in checks
###############

..  code-block:: python

    # continued from previous example...

    @yami.is_in_guild()
    @bot.command("add")
    async def add_cmd(ctx: yami.MessageContext, x: int, y: int) -> None:
        """Adds two numbers together."""
        await ctx.respond(f"{x} + {y} = {x + y}")

    @yami.has_roles("Supporter")
    @bot.command("slap", aliases=["smack"])
    async def slap_cmd(ctx: yami.MessageContext, user_id: int) -> None:
        """Slaps the user with the given id."""
        await ctx.respond(f"<@!{ctx.author.id}> slapped <@!{user_id}>!")

    @yami.is_owner()
    @bot.command("subtract", aliases=["sub", "minus"])
    async def slap_cmd(ctx: yami.MessageContext, x: int, y: int) -> None:
        """Subtracts y from x."""
        await ctx.respond(f"{x} - {y} = {x - y}")


#############
Custom checks
#############

There are quite a few ways to create custom checks:

 - Not yet documented.
