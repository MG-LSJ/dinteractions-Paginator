import random
from asyncio import TimeoutError
from typing import Optional, Union, List

import discord
from discord.ext import commands

from discord_slash import SlashContext
from discord_slash.context import ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button,
    wait_for_component,
    create_select, 
    create_select_option
)

from .errors import (
    BadContent,
    BadButtons,
    IncorrectDataType,
    BadEmoji,
    BadOnly,
    TooManyButtons
)


async def Paginator(
    bot: commands.Bot,
    ctx: Union[SlashContext, commands.Context],
    pages: List[discord.Embed],
    content: Optional[Union[str, List[str]]] = None,
    authorOnly: Optional[bool] = False,
    onlyFor: Optional[
            Union[
                discord.User,
                discord.Role,
                List[Union[discord.User, discord.Role]],
            ]
        ] = None,
    timeout: Optional[int] = None,
    disableAfterTimeout: Optional[bool] = True,
    deleteAfterTimeout: Optional[bool] = False,
    useSelect: Optional[bool] = True,
    useButtons: Optional[bool] = True,
    useIndexButton: Optional[bool] = False,
    useLinkButton: Optional[bool] = False,
    firstLabel: Optional[str] = "",
    prevLabel: Optional[str] = "",
    nextLabel: Optional[str] = "",
    indexLabel: Optional[str]="Page:",
    lastLabel: Optional[str] = "",
    linkLabel: Optional[Union[str, List[str]]] = "",
    linkURL: Optional[Union[str, List[str]]] = "",
    customButtonLabel: Optional[str] = None,
    firstEmoji: Optional[
        Union[discord.Emoji, discord.PartialEmoji, dict, bytes]
    ] = "⏮️",
    prevEmoji: Optional[
        Union[discord.Emoji, discord.PartialEmoji, dict, bytes]
    ] = "◀",
    nextEmoji: Optional[
        Union[discord.Emoji, discord.PartialEmoji, dict, bytes]
    ] = "▶",
    lastEmoji: Optional[
        Union[discord.Emoji, discord.PartialEmoji, dict, bytes]
    ] = "⏭️",
    customButtonEmoji: Optional[
        Union[discord.Emoji, discord.PartialEmoji, dict, bytes]
    ] = None,
    indexStyle: Optional[Union[ButtonStyle, int]] = 3,
    firstStyle: Optional[Union[ButtonStyle, int]] = 1,
    prevStyle: Optional[Union[ButtonStyle, int]] = 1,
    nextStyle: Optional[Union[ButtonStyle, int]] = 1,
    lastStyle: Optional[Union[ButtonStyle, int]] = 1,
    customButtonStyle: Optional[Union[ButtonStyle, int]] = 2,
):
    """
    :param bot: the bot/client variable with discord_slash.SlashCommand override
    :param ctx: command context
    :param content: the content of message to send
    :param authorOnly: paginator to work author only
    :param onlyFor: paginator to work for specified user(s)
    :param timeout: set paginator to work for limited time
    :param disableAfterTimeout: disables components after timeout
    :param deleteAfterTimeout: deletes components after timeout
    :param useSelect: uses select
    :param useButtons: uses buttons
    :param useIndexButton: uses index button
    :param useLinkButton: uses link button
    :param firstLabel: label of first page button
    :param prevLabel: label of previous page button
    :param indexLabel: label of the index button
    :param nextLabel: label of next page button
    :param lastLabel: label of last page button
    :param linkLabel: label of link button
    :param linkURL: URL of link button
    :param customButtonLabel: label of custom button
    :param firstEmoji: emoji of first page button
    :param prevEmoji: emoji of previous page button
    :param nextEmoji: emoji of next page button
    :param lastEmoji: emoji of last page button
    :param customButtonEmoji: emoji of custom button
    :param indexStyle: colo[u]r of index button
    :param firstStyle: colo[u]r of first button
    :param prevStyle: colo[u]r of previous button
    :param nextStyle: colo[u]r of next button
    :param lastStyle: colo[u]r of last button
    :param customButtonStyle: colo[u]r of custom button
    """
    top = len(pages)  # limit of the paginator
    multiContent = False
    multiLabel = False
    multiURL = False
    useCustomButton= False

    #ERROR HANDLING

    if not isinstance(bot, commands.Bot):
        raise IncorrectDataType("bot", "commands.Bot", bot)
    if not isinstance(ctx, SlashContext) and not isinstance(ctx, commands.Context):
        raise IncorrectDataType("ctx", "SlashContext or commands.Context", ctx)
    if isinstance(content, list):
        if len(content) < top:
            content = content[0]
            if not isinstance(content, str):
                raise BadContent(content)
        else:
            content = content[:top]
            for s in content:
                if not isinstance(s, str):
                    raise BadContent(content)
            multiContent = True
    elif not isinstance(content, str):
        if content != None:
            raise BadContent(content)
    if not isinstance(authorOnly, bool):
        raise IncorrectDataType("authorOnly", "bool", authorOnly)
    if not isinstance(onlyFor, discord.User):
        if not isinstance(onlyFor, discord.Role):
            if not isinstance(onlyFor, list):
                if onlyFor != None:
                    raise IncorrectDataType("onlyFor", "discord.User, discord.Role, or list of discord.User/discord.Role", onlyFor)
    if not isinstance(timeout, int):
        if timeout != None:
            raise IncorrectDataType("timeout", "int", timeout)
    if not isinstance(disableAfterTimeout, bool):
        raise IncorrectDataType("disableAfterTimeout", "bool", disableAfterTimeout)
    if not isinstance(deleteAfterTimeout, bool):
        raise IncorrectDataType("deleteAfterTimeout", "bool", deleteAfterTimeout)
    if not isinstance(useSelect, bool):
        raise IncorrectDataType("useSelect", "bool", useSelect)
    if not isinstance(useButtons, bool):
        raise IncorrectDataType("useButtons", "bool", useButtons)
    if not isinstance(useIndexButton, bool):
        raise IncorrectDataType("useIndexButton", "bool", useIndexButton)
    if not isinstance(useLinkButton, bool):
        raise IncorrectDataType("useLinkButton", "bool", useLinkButton)
    if not isinstance(firstLabel, str):
        raise IncorrectDataType("firstLabel", "str", firstLabel)
    if not isinstance(prevLabel, str):
        raise IncorrectDataType("prevLabel", "str", prevLabel)
    if not isinstance(nextLabel, str):
        raise IncorrectDataType("nextLabel", "str", nextLabel)
    if not isinstance(lastLabel, str):
        raise IncorrectDataType("lastLabel", "str", lastLabel)
    
    if isinstance(linkLabel, list):
        if len(linkLabel) < top:
            linkLabel = linkLabel[0]
            if not isinstance(linkLabel, str):
                raise IncorrectDataType("linkLabel", "str or list of str", linkLabel)
        else:
            linkLabel = linkLabel[:top]
            for s in linkLabel:
                if not isinstance(s, str):
                    raise IncorrectDataType("linkLabel", "str or list of str", linkLabel)
            multiLabel = True
    elif not isinstance(linkLabel, str):
        raise IncorrectDataType("linkLabel", "str or list of str", linkLabel)
    if isinstance(linkURL, list):
        if len(linkURL) < top:
            linkURL = linkURL[0]
            if not isinstance(linkURL, str):
                raise IncorrectDataType("linkURL", "str or list of str", linkURL)
        else:
            linkURL = linkURL[:top]
            for s in linkURL:
                if not isinstance(s, str):
                    raise IncorrectDataType("linkURL", "str or list of str", linkURL)
            multiURL = True
    elif not isinstance(linkURL, str):
        raise IncorrectDataType("linkURL", "str or list of str", linkURL)
    if not isinstance(customButtonLabel, str):
        if customButtonLabel != None:
            raise IncorrectDataType("customButtonLabel", "str", customButtonLabel)
    emojis = [firstEmoji, prevEmoji, nextEmoji, lastEmoji]
    for emoji in emojis:
        num = emojis.index(emoji) + 1
        if not isinstance(emoji, discord.Emoji) and not isinstance(emoji, discord.PartialEmoji) and not isinstance(emoji, dict) and not isinstance(emoji, str):
            raise BadEmoji(num)
    if not isinstance(indexStyle, ButtonStyle) and not isinstance(indexStyle, int):
        raise IncorrectDataType("indexStyle", "ButtonStyle or int", indexStyle)
    if not isinstance(firstStyle, ButtonStyle) and not isinstance(firstStyle, int):
        raise IncorrectDataType("firstStyle", "ButtonStyle or int", firstStyle)
    if not isinstance(prevStyle, ButtonStyle) and not isinstance(prevStyle, int):
        raise IncorrectDataType("prevStyle", "ButtonStyle or int", prevStyle)
    if not isinstance(nextStyle, ButtonStyle) and not isinstance(nextStyle, int):
        raise IncorrectDataType("nextStyle", "ButtonStyle or int", nextStyle)
    if not isinstance(lastStyle, ButtonStyle) and not isinstance(lastStyle, int):
        raise IncorrectDataType("lastStyle", "ButtonStyle or int", lastStyle)
    if not isinstance(customButtonStyle, ButtonStyle) and not isinstance(customButtonStyle, int):
        raise IncorrectDataType("customButtonStyle", "ButtonStyle or int", customButtonStyle)
    
    if useIndexButton and useLinkButton:
        BadButtons("Can not use index and link button at the same time!")
        useLinkButton = False

    if authorOnly and onlyFor:
        BadOnly()
        authorOnly = False
    
    if customButtonLabel != None:
        useCustomButton= True
    
    bid = random.randint(10000, 99999)  # base of button id
    index = 0  # starting page
    controlButtons = [
        # First button
        create_button(
            style=firstStyle,
            label=firstLabel,
            custom_id=f"{bid}-first",
            disabled=True,
            emoji=firstEmoji,
        ),
        # Previous Button
        create_button(
            style=prevStyle,
            label=prevLabel,
            custom_id=f"{bid}-prev",
            disabled=True,
            emoji=prevEmoji,
        ),
        # Index
        create_button(
            style=indexStyle,
            label=f"{indexLabel} {index+1}/{top}",
            disabled=True,
            custom_id=f"{bid}-index",
        ),
        # Next Button
        create_button(
            style=nextStyle,
            label=nextLabel,
            custom_id=f"{bid}-next",
            disabled=False,
            emoji=nextEmoji,
        ),
        # Last button
        create_button(
            style=lastStyle,
            label=lastLabel,
            custom_id=f"{bid}-last",
            disabled=False,
            emoji=lastEmoji,
        )
    ]
    select_options = []
    for i in pages:
        pageNum = pages.index(i) + 1
        try:
            title = i.title
            if title == discord.Embed.Empty:
                select_options.append(create_select_option(f"{pageNum}: Title not found", value=f"{pageNum}"))
            else:
                title = (title[:93] + "...") if len(title) > 96 else title
                select_options.append(create_select_option(f"{pageNum}: {title}", value=f"{pageNum}"))
        except Exception:
            select_options.append(create_select_option(f"{pageNum}: Title not found", value=f"{pageNum}"))
    if useIndexButton and not useButtons:
        BadButtons("Index button cannot be used with useButtons=False!")
    useIndexButton = False if not useButtons else useIndexButton
    if not useIndexButton:
        controlButtons.pop(2)
    if useLinkButton:
        linkButton = create_button(
            style=5,
            label=linkLabel[0] if multiLabel else linkLabel,
            url=linkURL[0] if multiURL else linkURL
        )
        if len(controlButtons) < 5:
            controlButtons.append(linkButton)
        else:
            raise TooManyButtons()
    if useCustomButton:
        customButton = create_button(
            style=customButtonStyle,
            label=customButtonLabel,
            disabled=True,
            emoji=customButtonEmoji
        )
        if len(controlButtons) < 5:
            controlButtons.append(customButton)
        else:
            raise TooManyButtons()
    buttonControls = create_actionrow(*controlButtons)
    components = []
    if useSelect:
        select = create_select(
            options=select_options,
            placeholder=f"Page {index+1}/{top}",
            min_values=1,
            max_values=1,
        )
        selectControls = create_actionrow(select)
        components.append(selectControls)
    if useButtons:
        components.append(buttonControls)
    msg = await ctx.send(content=content[0] if multiContent else content, embed=pages[0], components=components)
    # handling the interaction
    tmt = True  # stop listening when timeout expires
    while tmt:
        try:
            button_context: ComponentContext = await wait_for_component(
                bot, components=components, timeout=timeout
            )
        except TimeoutError:
            tmt = False
            if deleteAfterTimeout:
                await msg.edit(
                    components=None
                )
            elif disableAfterTimeout:
                if useSelect:
                    selectControls["components"][0][
                        "disabled"
                    ] = True
                for i in range(5 if useIndexButton else 4):
                    buttonControls["components"][i][
                        "disabled"
                    ] = True
                await msg.edit(
                    components=components
                )
        else:
            if authorOnly:
                if button_context.author.id != ctx.author.id:
                    await button_context.defer(ignore=True)
                    continue
            if onlyFor != None:
                check = False
                if isinstance(onlyFor, list):
                    for user in filter(
                        lambda x: isinstance(x, discord.abc.User), onlyFor
                    ):
                        check = check or user.id == button_context.author.id
                    for role in filter(
                        lambda x: isinstance(x, discord.role.Role), onlyFor
                    ):
                        check = check or role in button_context.author.roles
                else:
                    if isinstance(onlyFor, discord.abc.User):
                        check = check or onlyFor.id == button_context.author.id
                    elif isinstance(onlyFor, discord.role.Role):
                        check = check or onlyFor in button_context.author.roles
                if not check:
                    await button_context.defer(ignore=True)
                    continue
            await button_context.defer(edit_origin=True)
            # Handling first button
            if button_context.component_id == f"{bid}-first" and index > 0:
                index = 0  # first page
                buttonControls["components"][0][
                    "disabled"
                ] = True  # Disables the first button
                buttonControls["components"][1][
                    "disabled"
                ] = True  # Disables the previous button
                buttonControls["components"][3 if useIndexButton else 2]["disabled"] = False  # Enables Next Button
                buttonControls["components"][4 if useIndexButton else 3]["disabled"] = False  # Enables Last Button
                if useIndexButton:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useLinkButton:
                    if multiLabel:
                        buttonControls["components"][4][
                            "label"
                        ] = linkLabel[index]
                    if multiURL:
                        buttonControls["components"][4][
                            "url"
                        ] = linkURL[index]
                if useSelect:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content[index] if multiContent else content, embed=pages[index], components=components
                )
            # Handling previous button
            if button_context.component_id == f"{bid}-prev" and index > 0:
                index = index - 1  # lowers index by 1
                if index == 0:
                    buttonControls["components"][0][
                        "disabled"
                    ] = True  # Disables the first button
                    buttonControls["components"][1][
                        "disabled"
                    ] = True  # Disables the previous button
                buttonControls["components"][3 if useIndexButton else 2]["disabled"] = False  # Enables Next Button
                buttonControls["components"][4 if useIndexButton else 3]["disabled"] = False  # Enables Last Button
                if useIndexButton:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useLinkButton:
                    if multiLabel:
                        buttonControls["components"][4][
                            "label"
                        ] = linkLabel[index]
                    if multiURL:
                        buttonControls["components"][4][
                            "url"
                        ] = linkURL[index]
                if useSelect:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content[index] if multiContent else content, embed=pages[index], components=components
                )
            # handling next button
            if button_context.component_id == f"{bid}-next" and index < top - 1:
                index = index + 1  # add 1 to the index
                if index == top - 1:
                    buttonControls["components"][3 if useIndexButton else 2][
                        "disabled"
                    ] = True  # disables the next button
                    buttonControls["components"][4 if useIndexButton else 3][
                        "disabled"
                    ] = True  # disables the last button
                buttonControls["components"][0]["disabled"] = False  # enables first button
                buttonControls["components"][1]["disabled"] = False  # enables previous button
                if useIndexButton:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useLinkButton:
                    if multiLabel:
                        buttonControls["components"][4][
                            "label"
                        ] = linkLabel[index]
                    if multiURL:
                        buttonControls["components"][4][
                            "url"
                        ] = linkURL[index]
                if useSelect:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content[index] if multiContent else content, embed=pages[index], components=components
                )
            # handling last button
            if button_context.component_id == f"{bid}-last" and index < top - 1:
                index = top - 1  # set index to last
                buttonControls["components"][3 if useIndexButton else 2][
                    "disabled"
                ] = True  # disables the next button
                buttonControls["components"][4 if useIndexButton else 3][
                    "disabled"
                ] = True  # disables the last button
                buttonControls["components"][0]["disabled"] = False  # enables first button
                buttonControls["components"][1]["disabled"] = False  # enables previous button
                if useIndexButton:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useLinkButton:
                    if multiLabel:
                        buttonControls["components"][4][
                            "label"
                        ] = linkLabel[index]
                    if multiURL:
                        buttonControls["components"][4][
                            "url"
                        ] = linkURL[index]
                if useSelect:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content[index] if multiContent else content, embed=pages[index], components=components
                )
            # handling select
            if button_context.component_type == 3:
                index = int(button_context.selected_options[0]) - 1
                if useButtons:
                    if index == 0:
                        buttonControls["components"][0][
                            "disabled"
                        ] = True  # Disables the first button
                        buttonControls["components"][1][
                            "disabled"
                        ] = True  # Disables the previous button
                        buttonControls["components"][3 if useIndexButton else 2]["disabled"] = False  # Enables Next Button
                        buttonControls["components"][4 if useIndexButton else 3]["disabled"] = False  # Enables Last Button
                    elif index == top - 1:
                        buttonControls["components"][3 if useIndexButton else 2][
                            "disabled"
                        ] = True  # disables the next button
                        buttonControls["components"][4 if useIndexButton else 3][
                            "disabled"
                        ] = True  # disables the last button
                        buttonControls["components"][0]["disabled"] = False  # enables first button
                        buttonControls["components"][1]["disabled"] = False  # enables previous button
                    else:
                        buttonControls["components"][3 if useIndexButton else 2][
                            "disabled"
                        ] = False # enables the next button
                        buttonControls["components"][4 if useIndexButton else 3][
                            "disabled"
                        ] = False # enables the last button
                        buttonControls["components"][0]["disabled"] = False # enables first button
                        buttonControls["components"][1]["disabled"] = False # enables previous button
                    if useIndexButton:
                        buttonControls["components"][2][
                            "label"
                        ] = f"Page {index+1}/{top}"  # updates the index
                    if useLinkButton:
                        if multiLabel:
                            buttonControls["components"][4][
                                "label"
                            ] = linkLabel[index]
                        if multiURL:
                            buttonControls["components"][4][
                                "url"
                            ] = linkURL[index]
                if useSelect:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content[index] if multiContent else content, embed=pages[index], components=components
                )
