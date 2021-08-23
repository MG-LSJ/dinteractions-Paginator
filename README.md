# dinteractions-Paginator
Unofficial discord-interactions multi-page embed handler

[![Discord](https://img.shields.io/discord/859508565101248582?color=blue&label=discord&style=for-the-badge)](https://discord.gg/UYCaSsMewk) [![PyPI - Downloads](https://img.shields.io/pypi/dm/dinteractions-Paginator?color=blue&style=for-the-badge)](https://pypi.org/project/dinteractions-Paginator/)

## Table of Contents
- [Features](#feats)
- [Installation](#install)
- [Dependencies](#dep)
- [Examples](#examples)
  - [Example GIF:](#gif)
  - [Slash command:](#slash)
  - [Normal command:](#normal)
    - [Note](#note)
- [Paginator](#paginator)
- [TimedOut](#timed)
- [Credits](#credits)

### Join our [Discord server](https://discord.gg/UYCaSsMewk)!
- Try out all the possible combinations of the paginator with `/example1` and `/example2`,
- Ask some questions,
- And give us feedback and suggestions!

## <a name="feats"></a> Features
- Message per embed or persistent message
- Index select that can be turned on/off
- Select labels are generated based on embed's title
- Index button that can be turned on/off
- Ability to set the buttons to any emote, color or label

## <a name="install"></a> Installation
```
pip install -U dinteractions-Paginator
```

### <a name="dep"></a> Dependencies
- [discord.py](https://pypi.org/project/discord.py/) (version 1.7.3)
- [discord-interactions](https://pypi.org/project/discord-interactions/) (version 3.0.1 or 3.0.1a)

## <a name="examples"></a> Examples:
These simple examples show how to easily create interactive, multiple page embeds that annyone can interact with that automatically deactivate after 60 seconds of inactivity:

### <a name="gif"></a> Example GIF:
<div align="left">
    Paginator with select:<br>
    <img src="https://cdn.discordapp.com/attachments/871853650568417310/873731782514728980/o8YSi1nzvT.gif" height="400">
</div>

### <a name="slash"></a> Slash command:
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from dinteractions_Paginator import Paginator

bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@slash.slash(name="embeds")
async def embeds(ctx: SlashContext):
    one = discord.Embed(title="1st Embed", description="General Kenobi!", color=discord.Color.red())
    two = discord.Embed(title="2nd Embed", description="General Kenobi!", color=discord.Color.orange())
    three = discord.Embed(title="3rd Embed", description="General Kenobi!", color=discord.Color.gold())
    four = discord.Embed(title="4th Embed", description="General Kenobi!", color=discord.Color.green())
    five = discord.Embed(title="5th Embed", description="General Kenobi!", color=discord.Color.blue())
    pages = [one, two, three, four, five]

    await Paginator(bot=bot, ctx=ctx, pages=pages, content=["1", "2", "3", "4", "5"], timeout=60).run()

bot.run("token")
```

### <a name="normal"></a> Normal command:
```py
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from dinteractions_Paginator import Paginator

bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def embeds(ctx):
    one = discord.Embed(title="1st Embed", description="General Kenobi!", color=discord.Color.red())
    two = discord.Embed(title="2nd Embed", description="General Kenobi!", color=discord.Color.orange())
    three = discord.Embed(title="3rd Embed", description="General Kenobi!", color=discord.Color.gold())
    four = discord.Embed(title="4th Embed", description="General Kenobi!", color=discord.Color.green())
    five = discord.Embed(title="5th Embed", description="General Kenobi!", color=discord.Color.blue())
    pages = [one, two, three, four, five]

    await Paginator(bot=bot, ctx=ctx, pages=pages, content=["1", "2", "3", "4", "5"], timeout=60).run()

bot.run("token")
```
#### <a name="note"></a> **NOTE: `slash = SlashCommand(bot)` required to override `bot`**

## <a name="paginator"></a> *class* Paginator

### <a name="args"></a> Arguments

- [Required](#req)
- [Optional](#opt)
  - [Time](#time)
  - [What to use](#what)
  - [Labels](#labels)
  - [Emojis](#emojis)
  - [Styles](#styles)
- [Returns](#returns)

### <a name="req"></a> Required:
- `bot` - `commands.Bot`: The bot variable, `commands.Bot` is required
- `ctx` - `Union[commands.Context, SlashContext]`: The context of a command
- `pages` - `List[discord.Embed]`: A list of embeds to be paginated

------------------------------

### <a name="opt"></a> Optional:
- `content` - `Optional[Union[str, List[str]]]`: the content of the message to send, defaults to `None`
- `authorOnly` - `Optional[bool]`: if you want the paginator to work for the author only, default is `False`
- `onlyFor` - `Optional[Union[discord.User, discord.Role, List[Union[discord.User, discord.Role]]]]`: components only for specified user(s) or role(s)

#### <a name="time"></a> Time:
- `timeout` - `Optional[int]`: deactivates paginator after inactivity if enabled, defaults to `None` (meaning no timeout)
- `disableAfterTimeout` - `Optional[bool]`: disable components after `timeout`, default `True`
- `deleteAfterTimeout` - `Optional[bool]`: delete components after `timeout`, default `False`

#### <a name="what"></a> What to use:
- `useButtons` - `Optional[bool]`: uses buttons, default is `True`
- `useSelect` - `Optional[bool]`: uses a select, default is `True`
- `useIndexButton` - `Optional[bool]`: uses the index button, default is `False` and stays `False` if `useButtons` is also `False`
- `useLinkButton` - `Optional[bool]`: uses the link button
- `useFirstLast` - `Optional[bool]`: uses the first and last buttons, default `True`

#### <a name="labels"></a> Labels:
- `firstLabel` - `Optional[str]`: The label of the button used to go to the first page, defaults to `""`
- `prevLabel` - `Optional[str]`: The label of the button used to go to the previous page, defaults to `""`
- `indexLabel` - `Optional[str]`: The label of the index button, defaults to `"Page"`
- `nextLabel` - `Optional[str]`: The label of the button used to go to the next page, defaults to `""`
- `lastLabel` - `Optional[str]`: The label of the button used to go to the last page, defaults to `""`
- `linkLabel` - `Optional[Union[str, List[str]]]`: The label for the link button
- `linkURL` - `Optional[Union[str, List[str]]]`: The URL(s) for the link button
- `customButtonLabel` = `Optional[str]`: The label of a custom disabled button, default `None`

#### <a name="emojis"></a> Emojis:
- `firstEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, bytes]`: emoji of the button used to go to the first page, defaults to `"⏮️"`
- `prevEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, bytes]`: emoji of the button used to go to the previous page, defaults to `"◀"`
- `nextEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, bytes]`: emoji of the button used to go to the next page, defaults to `"▶"`
- `lastEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, bytes]`: emoji of the button used to go to the last page, defaults to `"⏭️"`
- `customButtonEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, bytes]`: emoji of the custom disabled button, defaults to `None`

#### <a name="styles"></a> Styles (the colo[u]r of the buttons):
- `firstStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the first button, defaults to `1` (`ButtonStyle.blue`)
- `prevStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the previous button, defaults to `1` (`ButtonStyle.blue`)
- `indexStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the index button, defaults to `3` (`ButtonStyle.green`)
- `nextStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the next button, defaults to `1` (`ButtonStyle.blue`)
- `lastStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the last button, defaults to `1` (`ButtonStyle.blue`)
- `customButtonStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the last button, defaults to `2` (`ButtonStyle.gray`)

### <a name="returns"></a> Returns
*class* TimedOut

------------------------------

## <a name="timed"></a> *class* TimedOut

### <a name="attrs"></a> Attributes
- `ctx` - `Union[commands.Context, SlashContext]`: The original context
- `buttonContext` - `ComponentContext`: The context for the paginator's components
- `timeTaken` - `int`: How long in seconds that user(s) used the paginator before the timeout
- `lastEmbed` - `discord.Embed`: The last embed that the paginator stopped at after timeout
- `successfulUsers` - `List[discord.User]`: Users that successfully used the paginator, the first user is the invoker
- `failedUsers` - `List[discord.User]`: Users that failed to use the paginator

-------------------------------

## <a name="credits"></a> Credits
- Contributors of [discord-interactions](https://pypi.org/project/discord-py-slash-command/)
    - [GitHub](https://github.com/discord-py-slash-commands/discord-py-interactions)
    - [Discord server](https://discord.gg/KkgMBVuEkx)
- [dpy-slash-button-paginator](https://pypi.org/project/dpy-slash-button-paginator/)
    - [GitHub](https://github.com/Catalyst4222/ButtonPaginator)
