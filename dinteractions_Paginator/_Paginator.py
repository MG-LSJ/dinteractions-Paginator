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


async def Paginator(
    bot: commands.Bot,
    ctx: SlashContext,
    pages: List[discord.Embed],
    content: Optional[str] = None,
    firstLabel: str = "",
    prevLabel: str = "",
    nextLabel: str = "",
    lastLabel: str = "",
    firstEmoji: Optional[
        Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict]
    ] = "⏮️",
    prevEmoji: Optional[
        Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict]
    ] = "◀",
    nextEmoji: Optional[
        Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict]
    ] = "▶",
    lastEmoji: Optional[
        Union[discord.emoji.Emoji, discord.partial_emoji.PartialEmoji, dict]
    ] = "⏭️",
    indexStyle: Optional[Union[ButtonStyle, int]] = 3,
    firstStyle: Optional[Union[ButtonStyle, int]] = 1,
    prevStyle: Optional[Union[ButtonStyle, int]] = 1,
    nextStyle: Optional[Union[ButtonStyle, int]] = 1,
    lastStyle: Optional[Union[ButtonStyle, int]] = 1,
    timeout: Optional[int] = None,
    authorOnly: Optional[bool] = False,
    useSelect: Optional[bool] = True,
    useIndexButton: Optional[bool] = False
):
    top = len(pages)  # limit of the paginator
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
            label=f"Page {index+1}/{top}",
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
            title = (title[:18] + "...") if len(title) > 21
            select_options.append(create_select_option(f"{pageNum}: {title}", value=f"{pageNum}"))
        except Exception:
            select_options.append(create_select_option(f"{pageNum}: Title not found", value=f"{pageNum}"))
    select = create_select(
        options=select_options,
        placeholder=f"Page {index+1}/{top}",
        min_values=1,
        max_values=1,
    )
    if useIndexButton == False:
        controlButtons.pop(2)
    selectControls = create_actionrow(select)
    buttonControls = create_actionrow(*controlButtons)
    components = [selectControls, buttonControls] if useSelect == True else [buttonControls]
    await ctx.send(content=content, embed=pages[0], components=components)
    # handling the interaction
    tmt = True  # stop listening when timeout expires
    while tmt:
        try:
            button_context: ComponentContext = await wait_for_component(
                bot, components=components, timeout=timeout
            )
            await button_context.defer(edit_origin=True)
        except TimeoutError:
            tmt = False
            await ctx.origin_message.edit(
                content=content, embed=pages[index], components=None
            )

        else:
            # Handling first button
            if button_context.component_id == f"{bid}-first" and index > 0:
                index = 0  # first page
                buttonControls["components"][0][
                    "disabled"
                ] = True  # Disables the first button
                buttonControls["components"][1][
                    "disabled"
                ] = True  # Disables the previous button
                buttonControls["components"][3 if useIndexButton == True else 2]["disabled"] = False  # Enables Next Button
                buttonControls["components"][4 if useIndexButton == True else 3]["disabled"] = False  # Enables Last Button
                if useIndexButton == True:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useSelect == True:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content, embed=pages[index], components=components
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
                buttonControls["components"][3 if useIndexButton == True else 2]["disabled"] = False  # Enables Next Button
                buttonControls["components"][4 if useIndexButton == True else 3]["disabled"] = False  # Enables Last Button
                if useIndexButton == True:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useSelect == True:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content, embed=pages[index], components=components
                )
            # handling next button
            if button_context.component_id == f"{bid}-next" and index < top - 1:
                index = index + 1  # add 1 to the index
                if index == top - 1:
                    buttonControls["components"][3 if useIndexButton == True else 2][
                        "disabled"
                    ] = True  # disables the next button
                    buttonControls["components"][4 if useIndexButton == True else 3][
                        "disabled"
                    ] = True  # disables the last button
                buttonControls["components"][0]["disabled"] = False  # enables first button
                buttonControls["components"][1]["disabled"] = False  # enables previous button
                if useIndexButton == True:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useSelect == True:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content, embed=pages[index], components=components
                )
            # handling last button
            if button_context.component_id == f"{bid}-last" and index < top - 1:
                index = top - 1  # set index to last
                buttonControls["components"][3 if useIndexButton == True else 2][
                    "disabled"
                ] = True  # disables the next button
                buttonControls["components"][4 if useIndexButton == True else 3][
                    "disabled"
                ] = True  # disables the last button
                buttonControls["components"][0]["disabled"] = False  # enables first button
                buttonControls["components"][1]["disabled"] = False  # enables previous button
                if useIndexButton == True:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useSelect == True:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content, embed=pages[index], components=components
                )
            # handling select
            if button_context.component_type == 3:
                index = int(button_context.selected_options[0]) - 1
                if index == 0:
                    buttonControls["components"][0][
                        "disabled"
                    ] = True  # Disables the first button
                    buttonControls["components"][1][
                        "disabled"
                    ] = True  # Disables the previous button
                    buttonControls["components"][3 if useIndexButton == True else 2]["disabled"] = False  # Enables Next Button
                    buttonControls["components"][4 if useIndexButton == True else 3]["disabled"] = False  # Enables Last Button
                elif index == top - 1:
                    buttonControls["components"][3 if useIndexButton == True else 2][
                        "disabled"
                    ] = True  # disables the next button
                    buttonControls["components"][4 if useIndexButton == True else 3][
                        "disabled"
                    ] = True  # disables the last button
                    buttonControls["components"][0]["disabled"] = False  # enables first button
                    buttonControls["components"][1]["disabled"] = False  # enables previous button
                else:
                    buttonControls["components"][3 if useIndexButton == True else 2][
                        "disabled"
                    ] = False # enables the next button
                    buttonControls["components"][4 if useIndexButton == True else 3][
                        "disabled"
                    ] = False # enables the last button
                    buttonControls["components"][0]["disabled"] = False # enables first button
                    buttonControls["components"][1]["disabled"] = False # enables previous button
                if useIndexButton == True:
                    buttonControls["components"][2][
                        "label"
                    ] = f"Page {index+1}/{top}"  # updates the index
                if useSelect == True:
                    selectControls["components"][0][
                        "placeholder"
                    ] = f"Page {index+1}/{top}"
                await button_context.edit_origin(
                    content=content, embed=pages[index], components=components
                )
