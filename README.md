# Paginator.py
 Unnoficial discord-interactions paginator

## Example
This simple example shows how to easily create interactive, multiple page embeds that annyone can interact with.
```py
import discord
import discord_slash
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import Paginator

@slash.slash(name="command")
async def command(ctx:SlashContext)
embed1=discord.Embed(title="title")
embed2=discord.Embed(title="another title")
embed3=discord.Embed(title="yet another title")
pages=[embed1,embed2,embed3]

await Paginator(bot=bot,ctx=ctx,pages=pages,content="Hello there")
```