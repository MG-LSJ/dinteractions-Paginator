# dinteractions-Paginator
Unofficial discord-interactions multi-page embed handler

## Installation
`pip install dinteractions-Paginator`

### Dependencies
- [discord.py](https://pypi.org/project/discord.py/)
- [discord-interactions](https://pypi.org/project/discord-interactions/)

## Example
This simple example shows how to easily create interactive, multiple page embeds that annyone can interact with.
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dinteractions_Paginator import Paginator

bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot, sync_commands=True)

@slash.slash(name="command")
async def command(ctx: SlashContext):
    embed1 = discord.Embed(title="Title")
    embed2 = discord.Embed(title="Another Title")
    embed3 = discord.Embed(title="Yet Another Title")
    pages = [embed1, embed2, embed3]

    await Paginator(bot=bot, ctx=ctx, pages=pages, content="Hello there")
 
bot.run("token")
```

## Arguments

- `bot` - The bot variable, `commands.Bot()` is required
- `ctx` - The context of a command; `SlashContext`
- `pages` - A list of embeds (`discord.Embed()`) to be paginated
- `content` - Optional: the content (`str`) of the message to send, defaults to `None`
- `prevLabel` - The label of the button (`str`) used to go to the previous page, defaults to `"Previous"`
- `nextLabel` - The label of the button (`str`) used to go to the next page, defaults to `"Next"`
- `prevEmoji` - Optional: emoji of the button (`discord.emoji.Emoji`, `discord.partial_emoji.PartialEmoji`, or `dict`) used to go to the previous page, defaults to `None`
- `nextEmoji` - Optional: emoji of the button (`discord.emoji.Emoji`, `discord.partial_emoji.PartialEmoji`, or `dict`) used to go to the next page, defaults to `None`
- `indexStyle` - Optional: the type of button (`ButtonStyle` or `int`) for the index button, defaults to `1` (`ButtonStyle.blue` or `ButtonStyle.blurple`)
- `prevStyle` - Optional: the type of button (`ButtonStyle` or `int`) for the previous button, defaults to `3` (`ButtonStyle.green`)
- `nextStyle` - Optional: the type of button (`ButtonStyle` or `int`) for the next button, defaults to `3` (`ButtonStyle.green`)
- `timeout` - Optional: if you want the paginator to work for a limited number of seconds, you can specify it here (`int`), defaults to `None` (meaning no timeout)
- `authorOnly` - Optional: if you want the paginator to work for the author only, default is `False`
