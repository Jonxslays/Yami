Yami
====

A command handler that complements Hikari.

Getting Started
===============

Installation
############

**Stable**

.. code-block:: bash

   pip install yami

   # Alternatively
   python -m pip install yami

**Development**

.. code-block:: bash

   pip install git+https://github.com/Jonxslays/Yami.git

Creating your first bot
#######################

.. code-block:: python

   import os

   import hikari
   import yami


   bot = yami.Bot(os.environ["TOKEN"], prefix="$")

   @bot.command("echo", "Says what you said")
   async def echo_cmd(ctx: yami.MessageContext, text: str) -> None:
      await ctx.respond(text)

   @bot.listen(hikari.StartedEvent)
   async def on_started(_: hikari.StartedEvent)
      bot.load_all_modules("./modules")
      print(f"Modules loaded. Latency: {bot.heartbeat_latency}")


   if __name__ == "__main__":
      bot.run()

.. automodule:: yami
   :members:

.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
