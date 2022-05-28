# dinteractions-Paginator

<!-- need a new gif -->
<!-- <img src="https://cdn.discordapp.com/attachments/871853650568417310/893303845587931176/dinteractions-Paginator_noloop.gif"></img> -->

Official interactions.py paginator

[![Discord](https://img.shields.io/discord/859508565101248582?color=blue&label=discord&style=for-the-badge)](https://discord.gg/UYCaSsMewk) [![PyPI - Downloads](https://img.shields.io/pypi/dm/dinteractions-Paginator?color=blue&style=for-the-badge)](https://pypi.org/project/dinteractions-Paginator/)

## <a id="top"></a> Table of Contents

- [Features](#feats)
- [Installation](#install)
- [Dependencies](#dep)
- [Examples](#examples)
  - [Example GIF:](#gif)
  - [Example](#example)
- [API Reference](#api)
- [Credits](#credits)

## <a id="feats"></a> Features

- Message per embed or persistent message
- Index select that can be turned on/off
- Select labels are generated based on embed's title
- Index button that can be turned on/off
- Ability to set the buttons to any emote, color or label
- Custom buttons

### Join our [Discord server](https://discord.gg/UYCaSsMewk)

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

## <a id="install"></a> Installation

```bash
pip install -U dinteractions-Paginator
```

### <a id="dep"></a> Dependencies

- [discord-py-interactions](https://pypi.org/project/discord-py-interactions/) (version >=4.2.0)
- [interactions-wait-for](https://pypi.org/project/interactions-wait-for/) (version >=1.0.4)

## <a id="examples"></a> Examples

These simple examples show how to easily create interactive, multiple page embeds that anyone can interact with that
automatically deactivate after 60 seconds of inactivity:

### <a id="gif"></a> Example GIF

Paginator with select:<br>
<img src="https://cdn.discordapp.com/attachments/871853650568417310/974513833399975966/DiscordCanary_Ps13PCo8B2.gif"></img>

### <a id="example"></a> Example

```py
from interactions import Client, CommandContext, Embed
from interactions.ext.paginator import Page, Paginator

client = Client("token")

@client.command(name="paginator", description="Paginator example")
async def paginator_example(ctx: CommandContext):
    await Paginator(
        client=client,
        ctx=ctx,
        pages=[
            Page("Content 1", Embed(title="One")),
            Page("Content 2", Embed(title="Two")),
            Page("Content 3"),
            Page(embeds=[Embed(title="Four"), Embed(title="Five")]),
        ],
    ).run()

client.start()
```

# <a id="api"></a> API Reference

## <a id="page"></a> Page

This is an individual page to be added to the paginator.

### Arguments

- `?content: str`: The content of the page.
- `?embeds: Embed | list[Embed]`: The embed(s) to be displayed on the page.
- `?title: str`: The title of the page displayed in the select menu.
  - Defaults to content or the title of the embed with an available title.

### Example

```py
from interactions import Embed
from interactions.ext.paginator import Page, Paginator

pages = [
    Page("Content 1", Embed(title="One")),
    Page("Content 2", Embed(title="Two")),
    Page("Content 3"),
    Page(embeds=[Embed(title="Four"), Embed(title="Five")]),
]
...
p = Paginator(..., pages=pages)
await p.run()

```

## <a id="paginator"></a> *class* Paginator

### <a id="args"></a> Arguments

- [Required](#req)
- [Optional](#opt)
- [Attributes](#p_attrs)
- [Returns](#returns)

### <a id="req"></a> Required

- `client: Client`: The client instance
- `ctx: CommandContext | ComponentContext`: The context
- `pages: list[Page]`: The pages to paginate.
  - Use a list of `Page` objects.

### <a id="opt"></a> Optional

- `?timeout: int`: The amount of time in seconds before the paginator automatically deactivates.
  - Defaults to 60 seconds.
  - When timed out, the paginator will automatically deactivate, and by default, the components will be disabled.
    - To modify this behavior, modify `disable_after_timeout` or `remove_after_timeout`.
- `?author_only: bool = False`: Whether the paginator should only be used by the author.
- `?use_buttons: bool = True`: Whether the paginator should use buttons.
- `?use_select: bool = True`: Whether the paginator should use the select menu.
- `?use_index: bool = False`: Whether the paginator should use the index button.
- `?extended_buttons: bool = True`: Whether the paginator should use extended buttons.
  - They are 2 buttons that skip to the beginning or the end.
- `?buttons: dict[str, Button]`: Custom buttons to use.
  - The keys need to be one of the following: first, prev, index, next, last.
  - You can use the `ButtonKind` enum for this purpose.
- `?placeholder: str = "Page"`: The placeholder to use for the select menu.
- `?disable_after_timeout: bool = True`: Whether the components should be disabled after the timeout.
- `?remove_after_timeout: bool = True`: Whether the components should be removed after the timeout.
- `?func_before_edit: Callable | Coroutine`: A function or coroutine that will be called before the embed is edited.
  - The function will be passed the `Paginator` and `ComponentContext` objects.
  - Raise `StopPaginator` to stop the paginator.
  - Return `False` to skip editing the paginator.
- `?func_after_edit: Callable | Coroutine`: A function or coroutine that will be called after the embed is edited.
  - The function will be passed the `Paginator` and `ComponentContext` objects.
  - Raise `StopPaginator` to stop the paginator.

### <a id="p_attrs"></a> Attributes

All the parameters listed above are stored as attributes in the `Paginator` object.

Additional attributes:

- `id: int`: The paginator's ID.
  - A number between `0` and `999,999,999` to ensure that the paginator is unique.
- `?component_ctx: ComponentContext`: The context of the paginator's components.
  - This is only available if or when a component is interacted with.
- `index: int`: The current index of the paginator.
  - This is the index of the current page.
- `top: int`: The index of the top page.
- `?message: Message`: The message that the paginator is using.
- `_msg: dict[str, ?Snowflake | int]`: A dict with the `message_id` and `channel_id` of the message.
- `_json: dict[str, Any]`: The JSON representation of the paginator.
  - You can utilize this to create a paginator dynamically by doing this:

  ```py
  p = Paginator(client, ctx, pages, ...)
  another = Paginator(**p._json)
  ```

### <a id="returns"></a> Returns

[*class* Data](#_data)

------------------------------

## <a id="_data"></a> *class* Data

### <a id="attrs"></a> Attributes

- `paginator: Paginator`: The `Paginator` object.
- `original_ctx: CommandContext | ComponentContext`: The original context supplied to the paginator.
- `component_ctx: ComponentContext`: The component context.
- `message: Message`: The message that was sent.

------------------------------

## <a id="buttonkind"></a> *class* ButtonKind

- `FIRST: "first"`: The first button.
- `PREVIOUS: "prev"`: The previous button.
- `INDEX: "index"`: The index button.
- `NEXT: "next"`: The next button.
- `LAST: "last"`: The last button.

------------------------------

## <a id="stoppaginator"></a> *error* StopPaginator

Raise this error in your function or coroutine to stop the paginator.

------------------------------

## <a id="credits"></a> Credits

- Contributors of [interactions.py](https://pypi.org/project/discord-py-slash-command/)
  - [GitHub](https://github.com/interactions-py/library)
  - [Discord server](https://discord.gg/KkgMBVuEkx)

[Back to top](#top)
