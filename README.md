# dinteractions-Paginator

<img src="https://cdn.discordapp.com/attachments/871853650568417310/893303845587931176/dinteractions-Paginator_noloop.gif"></img>

Unofficial discord-interactions multi-page embed handler

[![Discord](https://img.shields.io/discord/859508565101248582?color=blue&label=discord&style=for-the-badge)](https://discord.gg/UYCaSsMewk) [![PyPI - Downloads](https://img.shields.io/pypi/dm/dinteractions-Paginator?color=blue&style=for-the-badge)](https://pypi.org/project/dinteractions-Paginator/)

## Table of Contents

(Only works in the [GitHub](https://github.com/JUGADOR123/dinteractions-Paginator/) for some reason)

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

## <a name="feats"></a> Features

- Message per embed or persistent message
- Index select that can be turned on/off
- Select labels are generated based on embed's title
- Index button that can be turned on/off
- Ability to set the buttons to any emote, color or label
- Custom buttons

### Join our [Discord server](https://discord.gg/UYCaSsMewk)!

- Try out example commands,
- Ask some questions,
- And give us feedback and suggestions!

### Wanna contribute?

- Make an issue to:
    - say what feature you want to be added
    - file a bug report
- Make a pull request and:
    - describe what you added/removed
    - why you added/removed it
- Make sure you use the issue/PR template!

## <a name="install"></a> Installation

```
pip install -U dinteractions-Paginator
```

### <a name="dep"></a> Dependencies

- [discord.py](https://pypi.org/project/discord.py/) (version 1.7.3)
- [discord-py-interactions](https://pypi.org/project/discord-py-interactions/) (version 3.0.2)

## <a name="examples"></a> Examples:

These simple examples show how to easily create interactive, multiple page embeds that anyone can interact with that
automatically deactivate after 60 seconds of inactivity:

### <a name="gif"></a> Example GIF:

Paginator with select:<br>
<img src="https://cdn.discordapp.com/attachments/871853650568417310/882017626266697758/MDTxhoscwG.gif"></img>

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
- [Custom buttons](#howtocustom)
    - [Example customButton](#cusbut)
    - [Example customActionRow](#cusact)
    - [Example GIF](#customgif)

### <a name="req"></a> Required:

- `bot` - `commands.Bot`: The bot variable, `commands.Bot` is required
- `ctx`
    - `Union[SlashContext, commands.Context, ComponentContext, MenuContext, discord.channel.TextChannel, discord.User, discord.Member]`:
      The context of a command.
      <br>NOTE: if one of the latter 3 are used, there will always be a `This interaction failed` even though it was a
      success, due to no context to respond to

------------------------------

### <a name="opt"></a> Optional:

- `pages` - `Optional[List[discord.Embed]]`: the list of embeds to be paginated, defaults to `None` and paginates `content` instead
  <br>NOTE: `content` must be a list for paginating without `pages`!
- `content` - `Optional[Union[str, List[str]]]`: the content of the message to send, defaults to `None`
- `files` - `Optional[Union[discord.File, List[discord.File]]]`: files to send, defaults to `None`
- `hidden` - `Optional[bool]`: if you want the paginator to be hidden, default `False`
- `authorOnly` - `Optional[bool]`: if you want the paginator to work for the author only, default is `False`
- `onlyFor` - `Optional[Union[discord.User, discord.Role, List[Union[discord.User, discord.Role]]]]`: components only
  for specified user(s) or role(s)
- `dm` - `Optional[bool]`: if you want the paginator to be DM'ed, default `False`
- `customActionRow` - `Optional[List[Union[dict, Callable]]]`: a custom action row, see [this](#howtocustom) for more
  info, defaults to `None`

#### <a name="customstuff"></a> Custom:

- `customButton` - `Optional[List[Union[dict, Awaitable]]]`: a list of a create_button(...) and an awaitable function, default `None`
- `customButton` - `Optional[List[Union[dict, Awaitable]]]`: a list of an action row and an awaitable function, default `None`

See how to use these args [here](#howtocustom)!

#### <a name="time"></a> Time:

- `timeout` - `Optional[int]`: deactivates paginator after inactivity if enabled, defaults to `None` (meaning no
  timeout)
- `disableAfterTimeout` - `Optional[bool]`: disable components after `timeout`, default `True`
- `deleteAfterTimeout` - `Opti onal[bool]`: delete components after `timeout`, default `False`

#### <a name="what"></a> What to use:

- `useButtons` - `Optional[bool]`: uses buttons, default is `True`
- `useSelect` - `Optional[bool]`: uses a select, default is `True`
- `useIndexButton` - `Optional[bool]`: uses the index button, default is `False` and stays `False` if `useButtons` is
  also `False`
- `useLinkButton` - `Optional[bool]`: uses the link button
- `useQuitButton` - `Optional[bool]`: quit button to end the paginator, default `False`
- `useFirstLast` - `Optional[bool]`: uses the first and last buttons, default `True`
- `useOverflow` - `Optional[bool]`: uses the overflow action row if there are too many buttons, default `True`
- `useNotYours` - `Optional[bool]`: sends an ephemeral (hidden) message if the paginator is not yours (see authorOnly or
  onlyFor), default `True`

#### <a name="labels"></a> Labels:

- `firstLabel` - `Optional[str]`: The label of the button used to go to the first page, defaults to `""`
- `prevLabel` - `Optional[str]`: The label of the button used to go to the previous page, defaults to `""`
- `indexLabel` - `Optional[str]`: The label of the index button, defaults to `"Page"`
- `nextLabel` - `Optional[str]`: The label of the button used to go to the next page, defaults to `""`
- `lastLabel` - `Optional[str]`: The label of the button used to go to the last page, defaults to `""`
- `linkLabel` - `Optional[Union[str, List[str]]]`: The label for the link button
- `linkURL` - `Optional[Union[str, List[str]]]`: The URL(s) for the link button
- `quitButtonLabel` - `Optional[str]`: The label of the quit button, default `"Quit"`

#### <a name="emojis"></a> Emojis:

- `firstEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, str]`: emoji of the
  button used to go to the first page, defaults to `"⏮️"`
- `prevEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, str]`: emoji of the
  button used to go to the previous page, defaults to `"◀"`
- `nextEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, str]`: emoji of the
  button used to go to the next page, defaults to `"▶"`
- `lastEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, str]`: emoji of the
  button used to go to the last page, defaults to `"⏭️"`
- `quitButtonEmoji` - `Optional[Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict, str]`: emoji of the
  quit button, defaults to `None`

#### <a name="styles"></a> Styles (the colo[u]r of the buttons):

- `firstStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the first button,
  defaults to `1` (`ButtonStyle.blue`)
- `prevStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the previous
  button, defaults to `1` (`ButtonStyle.blue`)
- `indexStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the index button,
  defaults to `3` (`ButtonStyle.green`)
- `nextStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the next button,
  defaults to `1` (`ButtonStyle.blue`)
- `lastStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the last button,
  defaults to `1` (`ButtonStyle.blue`)
- `quitButtonStyle` - `Optional[Union[ButtonStyle, int]]`: the style of button (`ButtonStyle` or `int`) for the quit
  button, defaults to `4` (`ButtonStyle.red`)

### <a name="returns"></a> Returns

[*class* TimedOut](#timed)

### <a name="howtocustom"></a> More info on `customButton` and `customActionRow`:

#### <a name="cusbut"></a> You can define your own custom button, with its own code!

##### <a name="cusbutcode"></a> Example code:

```py
@slash.slash(name="custom-action-row")
async def _custom_action_row(ctx: SlashContext):
    # Embeds:
    pages = [
        discord.Embed(title="1"),
        discord.Embed(title="2"),
        discord.Embed(title="3"),
        discord.Embed(title="4"),
        discord.Embed(title="5"),
    ]

    # Custom button:
    custom_button = create_button(style=3, label="A Green Button")

    # Function:
    async def custom_function(self, button_ctx):  # Required arguments
        await button_ctx.send("test", hidden=True)
        await self.ctx.send("lol")

    # Paginator:
    await Paginator(
        bot,
        ctx,
        pages,
        timeout=60,
        customButton=[
            custom_button,
            custom_function,
        ],  # Note that custom_function is not called
    ).run()
```

The code above runs a normal paginator, with 1 extra action row at the bottom!

#### <a name="cusact"></a> You can define your own custom action row, with its own code!

##### <a name="cusactcode"></a> Example code:

```py
@slash.slash(name="custom-action-row")
async def _custom_action_row(ctx: SlashContext):
    # Embeds:
    pages = [
        discord.Embed(title="1"),
        discord.Embed(title="2"),
        discord.Embed(title="3"),
        discord.Embed(title="4"),
        discord.Embed(title="5"),
    ]

    # Action row:
    buttons = [
        create_button(style=3, label="A Green Button"),
    ]
    custom_action_row = create_actionrow(*buttons)

    # Function:
    async def custom_function(self, button_ctx):  # Required arguments
        await button_ctx.send("test", hidden=True)
        await self.ctx.send("lol")

    # Paginator:
    await Paginator(
        bot,
        ctx,
        pages,
        timeout=60,
        customActionRow=[
            custom_action_row,
            custom_function,
        ],  # Note that custom_function is not called
    ).run()
```

The code above runs a normal paginator, with 1 extra action row at the bottom!

#### <a name="customgif"></a> Example GIF:

<img src="http://can-you-pls.just-click.download/r/ku7l7zjoc9a.gif"></img>

You can access all of the attributes of [*class* Paginator](#paginator) with `self`, such as the original command's
context (`self.ctx`), the bot variable (`self.bot`), and other things that you passed into it!

------------------------------

## <a name="timed"></a> *class* TimedOut

### <a name="attrs"></a> Attributes

- `ctx` - `Union[commands.Context, SlashContext]`: The original context
- `buttonContext` - `ComponentContext`: The context for the paginator's components
- `timeTaken` - `int`: How long in seconds that user(s) used the paginator before the timeout
- `lastContent` - `str`: The last content that the paginator stopped at after timeout
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
