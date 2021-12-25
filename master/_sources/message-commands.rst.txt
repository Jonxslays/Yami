================
Message commands
================

########################
Create a message command
########################

The bot listens for the
:obj:`~hikari.events.message_events.MessageCreateEvent` event. If the
message content begins with one of the bots prefixes and a command name
immediately following that, the bot will attempt to invoke the commands
callback.

..  note::

    Yami converts type hints in your callbacks function signature for
    basic Python types automatically.

    Convertible types:
    :obj:`int` :obj:`bool` :obj:`float` :obj:`complex` :obj:`bytes`

..  code-block:: python

    # continued from previous example...

    @bot.command("echo", aliases=["say"], invoke_with=True)
    async def echo_cmd(ctx: yami.MessageContext, text: str) -> None:
        """Echos what you said back to you."""
        await ctx.message.delete()
        ctx.shared.message = await ctx.respond(text)

###########################
Create a message subcommand
###########################

Subcommands in Yami do not have a special class. The only designation
they receive is the :obj:`~yami.MessageCommand.is_subcommand` and the
:obj:`~yami.MessageCommand.parent` properties.

..  note::
    The :obj:`~yami.MessageCommand.subcommand` decorator should be used
    as a method of the callback function of the parent command.

    - Subcommands must also pass each :obj:`~yami.Check` bound to its
      parent commands.

In this example the subcommand provides and optional interface to delete
the message sent by the parent command.

..  code-block:: python

    # continued from previous example...

    @echo_cmd.subcommand("-d", aliases=["--delete"])
    async def echo_delete_cmd(
        ctx: yami.MessageContext, _: str, timeout: float = 10.0
    ) -> None:
        """Optionally deletes the message after the given timeout."""
        if m := ctx.shared.message:
            await asyncio.sleep(timeout)
            await ctx.rest.delete_message(ctx.channel_id, m)
        else:
            await ctx.respond("Something went wrong - no message to delete.")

###############
Sub-subcommands
###############

You can chain subcommands down as far as you would like. There is nothing
holding you back :).

..  warning::

    Chaining subcommands does have some side effects to be aware of.

    - The ``allow_extra_args`` kwarg for :obj:`~yami.Bot` is very
      helpful for allowing you to align the arguments of your
      subcommands.

    - By default Yami disables the parent commands callback for any
      is disabled. This can be set using the ``invoke_with`` kwarg in
      the :obj:`yami.command`, :obj:`yami.Bot.command`, and
      :obj:`yami.MessageCommand.subcommand` decorators.

    - Varying number and type for arguments in the command callbacks
      can cause failures. Pay close attention to what type hints and
      what argument positions you occupy in each callback, as well as
      what defaults you set.

    - :obj:`yami.MessageContext.shared` can be a powerful tool when used
      to share information between parent commands and their
      subcommands. Keep in mind that if something goes wrong in the
      first callback, you may receive a :obj:`~yami.SharedNone` if you
      access an attribute that has not been set.

- Not yet fully documented
