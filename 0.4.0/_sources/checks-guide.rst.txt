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

Head over to the `checks reference <reference.html#module-yami.checks>`_
to see all the available built in checks.

..  code-block:: python

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

    @yami.has_perms(ban_members=True)
    @bot.command("ban")
    async def ban_cmd(ctx: yami.MessageContext, user_id: int) -> None:
        """Bans a member from the server."""

        # NOTE: there is not yet a bot_has_perms check which could
        # cause problems here.
        try:
            await ctx.rest.ban_user(ctx.guild_id, user_id)
        except Exception as e:
            await ctx.respond(f"Something went wrong: {e}", reply=True)
        else:
            await ctx.respond("Done!", reply=True)

#############
Custom checks
#############

Custom checks are the great way to exert a little more control over who
can run your commands.

..  note::

    A custom check is considered to fail if it returns ``False``, or
    raises an exception. If the check returns ``True`` or any other
    value (including ``None``) without raising an error, it will pass.

    Subclassed checks work a little different, see below for more info.

There are a few ways to create custom checks:

- Using a lambda function:

..  code-block:: python

    @yami.custom_check(lambda ctx: ctx.guild_id is not None)
    @bot.command("guild")
    async def guild_only(ctx: yami.MessageContext) -> None:
        await ctx.respond("Yep were in a guild!")

- Using a sync/async callback function:

..  code-block:: python

    async def guild_check(ctx: yami.MessageContext) -> bool | None:
        if not ctx.guild_id:
            return False

    @yami.custom_check(guild_check, message="This command is guild only!")
    @bot.command("guild")
    async def guild_only(ctx: yami.MessageContext) -> None:
        await ctx.respond("Yep were in a guild!")

- Using your own :obj:`~yami.Check` subclass:

..  warning::

    - If you subclass :obj:`~yami.Check` it is required that your
      subclass has an async method called ``execute`` that accepts one
      parameter, a :obj:`~yami.MessageContext`.

    - If the ``execute`` method :ul:`does not` raise any exception, it
      is considered :ul:`passed`. Make sure you raise an exception if
      you want the check to fail.

..  code-block:: python

    class MyGuildCheck(yami.Check):
        async def execute(self, ctx: yami.MessageContext) -> None:
            if not ctx.guild_id:
                raise yami.CheckFailed("Were not in a guild!")

    @yami.custom_check(MyCustomGuildCheck)
    @bot.command("guild")
    async def guild_only(ctx: yami.MessageContext) -> None:
        await ctx.respond("Yep were in a guild!")

Now go make sure your community isn't banning each other via your bot! :D
