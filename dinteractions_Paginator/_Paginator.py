from asyncio import TimeoutError, get_running_loop
from time import time
from typing import List, Optional, Union, Callable
from random import randint

from discord import Embed, Emoji, Member, PartialEmoji, Role, TextChannel, User
from discord.abc import User as userUser
from discord.ext.commands import AutoShardedBot, Bot, Context
from discord.role import Role as roleRole
from discord_slash.context import ComponentContext, InteractionContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import (
    create_actionrow,
    create_button,
    create_select,
    create_select_option,
    wait_for_component,
)

from .errors import (
    BadButtons,
    BadOnly,
    IncorrectDataType,
    TooManyButtons,
)


class TimedOut:
    def __init__(
        self,
        ctx: Union[
            InteractionContext,
            Context,
            TextChannel,
            User,
            Member,
        ],
        buttonContext: ComponentContext,
        timeTaken: int,
        lastContent: str,
        lastEmbed: Embed,
        successfulUsers: List[User],
        failedUsers: List[User],
    ):
        self.ctx = ctx
        self.buttonContext = buttonContext
        self.timeTaken = timeTaken
        self.lastContent = lastContent
        self.lastEmbed = lastEmbed
        self.successfulUsers = successfulUsers
        self.failedUsers = failedUsers


class Paginator:
    def __init__(
        self,
        bot: Union[AutoShardedBot, Bot],
        ctx: Union[
            InteractionContext,
            Context,
            TextChannel,
            User,
            Member,
        ],
        pages: List[Embed],
        content: Optional[Union[str, List[str]]] = None,
        hidden: Optional[bool] = False,
        authorOnly: Optional[bool] = False,
        onlyFor: Optional[
            Union[
                User,
                Role,
                List[Union[User, Role]],
            ]
        ] = None,
        dm: Optional[bool] = False,
        customActionRow: Optional[List[Union[dict, Callable]]] = None,
        timeout: Optional[int] = None,
        disableAfterTimeout: Optional[bool] = True,
        deleteAfterTimeout: Optional[bool] = False,
        useSelect: Optional[bool] = True,
        useButtons: Optional[bool] = True,
        useIndexButton: Optional[bool] = None,
        useLinkButton: Optional[bool] = False,
        useQuitButton: Optional[bool] = False,
        useFirstLast: Optional[bool] = True,
        useOverflow: Optional[bool] = True,
        useNotYours: Optional[bool] = True,
        firstLabel: Optional[str] = "",
        prevLabel: Optional[str] = "",
        indexLabel: Optional[str] = "Page",
        nextLabel: Optional[str] = "",
        lastLabel: Optional[str] = "",
        linkLabel: Optional[Union[str, List[str]]] = "",
        linkURL: Optional[Union[str, List[str]]] = "",
        customButtonLabel: Optional[str] = None,
        quitButtonLabel: Optional[str] = "Quit",
        firstEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "⏮️",
        prevEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "◀",
        nextEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "▶",
        lastEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "⏭️",
        customButtonEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = None,
        quitButtonEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = None,
        firstStyle: Optional[Union[ButtonStyle, int]] = 1,
        prevStyle: Optional[Union[ButtonStyle, int]] = 1,
        indexStyle: Optional[Union[ButtonStyle, int]] = 2,
        nextStyle: Optional[Union[ButtonStyle, int]] = 1,
        lastStyle: Optional[Union[ButtonStyle, int]] = 1,
        customButtonStyle: Optional[Union[ButtonStyle, int]] = 2,
        quitButtonStyle: Optional[Union[ButtonStyle, int]] = 4,
    ) -> TimedOut:
        self.bot = bot
        self.ctx = ctx
        self.pages = pages
        self.content = content
        self.hidden = hidden
        self.authorOnly = authorOnly
        self.onlyFor = onlyFor
        self.dm = dm
        self.timeout = timeout
        self.disableAfterTimeout = disableAfterTimeout
        self.deleteAfterTimeout = deleteAfterTimeout
        self.useSelect = useSelect
        self.useButtons = useButtons
        self.useIndexButton = useIndexButton
        self.useLinkButton = useLinkButton
        self.useQuitButton = useQuitButton
        self.useFirstLast = useFirstLast
        self.useOverflow = useOverflow
        self.useNotYours = useNotYours
        self.labels = [firstLabel, prevLabel, indexLabel, nextLabel, lastLabel]
        self.links = [linkLabel, linkURL]
        self.custom = [customButtonStyle, customButtonLabel, customButtonEmoji]
        self.quit = [quitButtonStyle, quitButtonLabel, quitButtonEmoji]
        self.emojis = [firstEmoji, prevEmoji, nextEmoji, lastEmoji]
        self.styles = [firstStyle, prevStyle, indexStyle, nextStyle, lastStyle]
        self.customActionRow = customActionRow

        self.top = len(self.pages)  # limit of the paginator
        self.multiContent = False
        self.multiLabel = False
        self.multiURL = False
        self.useCustomButton = False
        try:
            self.successfulUsers = [ctx.author]
        except AttributeError:
            self.successfulUsers = [ctx]
        self.failedUsers = []

        self.usedLink = self.usedCustom = self.usedQuit = False

        self.index = 1
        self.random_id = randint(1, 999999)

        # ERROR HANDLING

        self.incdata(
            "bot",
            self.bot,
            (AutoShardedBot, Bot),
            "commands.Bot or commands.AutoShardedBot",
        )
        self.incdata(
            "ctx",
            self.ctx,
            (InteractionContext, Context, TextChannel, User, Member),
            "InteractionContext, commands.Context, discord.TextChannel, discord.User, or discord.Member",
        )
        self.incdata(
            "content", self.content, (list, str, type(None)), "str or list(str)"
        )
        self.incdata("hidden", self.hidden, bool, "bool")
        self.incdata("authorOnly", self.authorOnly, bool, "bool")
        self.incdata(
            "onlyFor",
            self.onlyFor,
            (User, Role, list, type(None)),
            "discord.User/Role, or list(discord.User/Role)",
        )
        self.incdata("dm", self.dm, bool, "bool")
        self.incdata("timeout", self.timeout, (int, type(None)), "int")
        bools = {
            "disableAfterTimeout": self.disableAfterTimeout,
            "deleteAfterTimeout": self.deleteAfterTimeout,
            "useSelect": self.useSelect,
            "useButtons": self.useButtons,
            "useLinkButton": self.useLinkButton,
            "useQuitButton": self.useQuitButton,
            "useFirstLast": self.useFirstLast,
            "useOverflow": self.useOverflow,
            "useNotYours": self.useNotYours,
        }
        for b in bools:
            self.incdata(
                b,
                bools[b],
                bool,
                "bool",
            )
        self.incdata("useIndexButton", self.useIndexButton, (bool, type(None)), "bool")
        labels = {
            "firstLabel": firstLabel,
            "prevLabel": prevLabel,
            "indexLabel": indexLabel,
            "nextLabel": nextLabel,
            "lastLabel": lastLabel,
            "linkLabel": linkLabel,
            "linkURL": linkURL,
            "quitButtonLabel": quitButtonLabel,
        }
        for label in labels:
            self.incdata(
                label,
                labels[label],
                str,
                "str",
            )
        self.incdata("customButtonLabel", customButtonLabel, (str, type(None)), "str")
        self.incdata(
            "quitButtonEmoji",
            quitButtonEmoji,
            (Emoji, PartialEmoji, dict, str, type(None)),
            "Emoji, PartialEmoji, dict, str, or None",
        )
        emojis = {
            "firstEmoji": firstEmoji,
            "prevEmoji": prevEmoji,
            "nextEmoji": nextEmoji,
            "lastEmoji": lastEmoji,
        }
        for emoji in emojis:
            self.incdata(
                emoji,
                emojis[emoji],
                (Emoji, PartialEmoji, dict, str),
                "Emoji, PartialEmoji, dict, or str",
            )
        styles = {
            "firstStyle": firstStyle,
            "prevStyle": prevStyle,
            "indexStyle": indexStyle,
            "nextStyle": nextStyle,
            "lastStyle": lastStyle,
            "quitButtonStyle": quitButtonStyle,
        }
        for style in styles:
            self.incdata(
                style,
                styles[style],
                (ButtonStyle, int),
                "ButtonStyle or int",
            )
        self.incdata(
            "customActionRow",
            self.customActionRow,
            (list, type(None)),
            "a list with the action row, then the function",
        )

        if self.useIndexButton and not self.useButtons:
            BadButtons("Index button cannot be used with useButtons=False!")
            self.useIndexButton = False

        if self.authorOnly and self.onlyFor:
            BadOnly()
            self.authorOnly = False

        if customButtonLabel is not None:
            self.useCustomButton = True

        if self.useSelect and len(self.pages) > 25:
            self.useSelect = False
            if self.useIndexButton is None:
                self.useIndexButton = True

    async def run(self) -> TimedOut:
        self.usedLink = self.usedCustom = self.usedQuit = False
        try:
            if self.dm:
                if isinstance(self.ctx, InteractionContext) or isinstance(
                    self.ctx, Context
                ):
                    msg = await self.ctx.author.send(
                        content=self.content[0] if self.multiContent else self.content,
                        embed=self.pages[0],
                        components=self.components(),
                        hidden=self.hidden,
                    )
                    await self.ctx.send("Check your DMs!", hidden=True)
                elif isinstance(self.ctx, userUser):
                    msg = await self.ctx.send(
                        content=self.content[0] if self.multiContent else self.content,
                        embed=self.pages[0],
                        components=self.components(),
                        hidden=self.hidden,
                    )
                else:
                    IncorrectDataType(
                        "ctx",
                        "InteractionContext or commands.Context for dm=True",
                        self.ctx,
                    )
            else:
                msg = await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embed=self.pages[0],
                    components=self.components(),
                    hidden=self.hidden,
                )
        except TypeError:
            if self.dm:
                if isinstance(self.ctx, InteractionContext) or isinstance(
                    self.ctx, Context
                ):
                    msg = await self.ctx.author.send(
                        content=self.content[0] if self.multiContent else self.content,
                        embed=self.pages[0],
                        components=self.components(),
                    )
                    await self.ctx.send("Check your DMs!", hidden=True)
                elif isinstance(self.ctx, userUser):
                    msg = await self.ctx.send(
                        content=self.content[0] if self.multiContent else self.content,
                        embed=self.pages[0],
                        components=self.components(),
                    )
                else:
                    IncorrectDataType(
                        "ctx", "InteractionContext or commands.Context", self.ctx
                    )
            else:
                msg = await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embed=self.pages[0],
                    components=self.components(),
                )
        tmt = True
        start = time()
        buttonContext = None
        while tmt:
            try:
                buttonContext: ComponentContext = await wait_for_component(
                    self.bot,
                    check=self.check,
                    components=self.components(),
                    timeout=self.timeout,
                )
                if buttonContext.author not in self.successfulUsers:
                    self.successfulUsers.append(buttonContext.author)
                if buttonContext.custom_id == f"first{self.random_id}":
                    self.index = 1
                elif buttonContext.custom_id == f"prev{self.random_id}":
                    self.index = self.index - 1 or 1
                elif buttonContext.custom_id == f"next{self.random_id}":
                    self.index = self.index + 1 or self.top
                elif buttonContext.custom_id == f"last{self.random_id}":
                    self.index = self.top
                elif buttonContext.custom_id == f"select{self.random_id}":
                    self.index = int(buttonContext.selected_options[0])
                elif buttonContext.custom_id == f"quit{self.random_id}":
                    tmt = False
                    end = time()
                    if self.deleteAfterTimeout and not self.hidden:
                        await buttonContext.origin_message.delete()
                    elif self.disableAfterTimeout and not self.hidden:
                        components = self.components()
                        for row in components:
                            for component in row["components"]:
                                component["disabled"] = True
                        await buttonContext.edit_origin(components=components)
                    timeTaken = round(end - start)
                    lastContent = (
                        self.content
                        if isinstance(self.content, (str, type(None)))
                        else self.content[self.index - 1]
                    )
                    lastEmbed = self.pages[self.index - 1]
                    return TimedOut(
                        self.ctx,
                        buttonContext,
                        timeTaken,
                        lastContent,
                        lastEmbed,
                        self.successfulUsers,
                        self.failedUsers,
                    )
                elif self.customActionRow is not None:
                    await self.customActionRow[1](self, buttonContext)
                    continue

                await buttonContext.edit_origin(
                    content=self.content[self.index - 1]
                    if self.multiContent
                    else self.content,
                    embed=self.pages[self.index - 1],
                    components=self.components(),
                )
            except TimeoutError:
                tmt = False
                end = time()
                if self.deleteAfterTimeout and not self.hidden:
                    await msg.edit(components=None)
                elif self.disableAfterTimeout and not self.hidden:
                    components = self.components()
                    for row in components:
                        for component in row["components"]:
                            component["disabled"] = True
                    await msg.edit(components=components)
                timeTaken = round(end - start)
                lastContent = (
                    self.content
                    if isinstance(self.content, (str, type(None)))
                    else self.content[self.index - 1]
                )
                lastEmbed = self.pages[self.index - 1]
                return TimedOut(
                    self.ctx,
                    buttonContext,
                    timeTaken,
                    lastContent,
                    lastEmbed,
                    self.successfulUsers,
                    self.failedUsers,
                )

    def check(self, buttonContext) -> bool:
        if self.authorOnly and buttonContext.author.id != self.ctx.author.id:
            if buttonContext.author not in self.failedUsers:
                if self.useNotYours:
                    get_running_loop().create_task(
                        buttonContext.send(
                            f"{buttonContext.author.mention}, this paginator is not for you!",
                            hidden=True,
                        )
                    )
                self.failedUsers.append(buttonContext.author)
            return False
        if self.onlyFor is not None:
            check = False
            if isinstance(self.onlyFor, list):
                for user in filter(lambda x: isinstance(x, userUser), self.onlyFor):
                    check = check or user.id == buttonContext.author.id
                for role in filter(lambda x: isinstance(x, roleRole), self.onlyFor):
                    check = check or role in buttonContext.author.roles
            else:
                if isinstance(self.onlyFor, userUser):
                    check = check or self.onlyFor.id == buttonContext.author.id
                elif isinstance(self.onlyFor, roleRole):
                    check = check or self.onlyFor in buttonContext.author.roles

            if not check:
                if self.useNotYours:
                    get_running_loop().create_task(
                        buttonContext.send(
                            f"{buttonContext.author.mention}, this paginator is not for you!",
                            hidden=True,
                        )
                    )
                self.failedUsers.append(buttonContext.author)
                return False

        return True

    def select_row(self) -> dict:
        select_options = []
        for i in self.pages:
            pageNum = self.pages.index(i) + 1
            try:
                title = i.title
                if title == Embed.Empty:
                    select_options.append(
                        create_select_option(
                            f"{pageNum}: Title not found", value=f"{pageNum}"
                        )
                    )
                else:
                    title = (title[:93] + "...") if len(title) > 96 else title
                    select_options.append(
                        create_select_option(f"{pageNum}: {title}", value=f"{pageNum}")
                    )
            except Exception:
                select_options.append(
                    create_select_option(
                        f"{pageNum}: Title not found", value=f"{pageNum}"
                    )
                )
        select = create_select(
            options=select_options,
            custom_id=f"select{self.random_id}",
            placeholder=f"{self.labels[2]} {self.index}/{self.top}",
            min_values=1,
            max_values=1,
        )
        selectControls = create_actionrow(select)
        return selectControls

    def buttons_row(self) -> dict:
        disableLeft = self.index == 1
        disableRight = self.index == self.top
        controlButtons = [
            # Previous Button
            create_button(
                style=self.styles[1],
                label=self.labels[1],
                custom_id=f"prev{self.random_id}",
                disabled=disableLeft,
                emoji=self.emojis[1],
            ),
            # Index
            create_button(
                style=self.styles[2],
                label=f"{self.labels[2]} {self.index}/{self.top}",
                disabled=True,
            ),
            # Next Button
            create_button(
                style=self.styles[3],
                label=self.labels[3],
                custom_id=f"next{self.random_id}",
                disabled=disableRight,
                emoji=self.emojis[2],
            ),
        ]
        if not self.useIndexButton:
            controlButtons.pop(1)
        if self.useFirstLast:
            # First button
            controlButtons.insert(
                0,
                create_button(
                    style=self.styles[0],
                    label=self.labels[0],
                    custom_id=f"first{self.random_id}",
                    disabled=disableLeft,
                    emoji=self.emojis[0],
                ),
            )
            # Last button
            controlButtons.append(
                create_button(
                    style=self.styles[4],
                    label=self.labels[4],
                    custom_id=f"last{self.random_id}",
                    disabled=disableRight,
                    emoji=self.emojis[3],
                )
            )
        if self.useLinkButton:
            linkButton = create_button(
                style=5,
                label=self.links[0][0] if self.multiLabel else self.links[0],
                url=self.links[1][0] if self.multiURL else self.links[1],
            )
            if len(controlButtons) < 5:
                controlButtons.append(linkButton)
                self.usedLink = True
            elif not self.useOverflow:
                raise TooManyButtons()
        if self.useCustomButton:
            customButton = create_button(
                style=self.custom[0],
                label=self.custom[1],
                disabled=True,
                emoji=self.custom[2],
            )
            if len(controlButtons) < 5:
                controlButtons.append(customButton)
                self.usedCustom = True
            elif not self.useOverflow:
                raise TooManyButtons()
        if self.useQuitButton:
            quitButton = create_button(
                style=self.quit[0],
                label=self.quit[1],
                emoji=self.quit[2],
                custom_id=f"quit{self.random_id}",
            )
            if len(controlButtons) < 5:
                controlButtons.append(quitButton)
                self.usedCustom = True
            elif not self.useOverflow:
                raise TooManyButtons()
        return create_actionrow(*controlButtons)

    def overflow_row(self) -> dict:
        controlButtons = []
        if self.useLinkButton and not self.usedLink:
            linkButton = create_button(
                style=5,
                label=self.links[0][0] if self.multiLabel else self.links[0],
                url=self.links[1][0] if self.multiURL else self.links[1],
            )
            if len(controlButtons) < 5:
                controlButtons.append(linkButton)
        if self.useCustomButton and not self.usedCustom:
            customButton = create_button(
                style=self.custom[0],
                label=self.custom[1],
                disabled=True,
                emoji=self.custom[2],
            )
            if len(controlButtons) < 5:
                controlButtons.append(customButton)
        if self.useQuitButton and not self.usedCustom:
            quitButton = create_button(
                style=self.quit[0],
                label=self.quit[1],
                emoji=self.quit[2],
                custom_id=f"quit{self.random_id}",
            )
            if len(controlButtons) < 5:
                controlButtons.append(quitButton)
        return None if controlButtons == [] else create_actionrow(*controlButtons)

    def components(self) -> list:
        return list(
            filter(
                None,
                [
                    self.select_row() if self.useSelect else None,
                    self.buttons_row() if self.useButtons else None,
                    self.overflow_row() if self.useOverflow else None,
                    None if self.customActionRow is None else self.customActionRow[0],
                ],
            )
        )

    def incdata(self, name, arg, sup, supstr) -> None:
        if isinstance(arg, tuple) and isinstance(sup, tuple):
            for a in arg:
                if isinstance(a, sup):
                    return
                else:
                    raise IncorrectDataType(name[arg.index(a)], supstr, a)
        elif isinstance(arg, tuple):
            for a in arg:
                if isinstance(a, sup):
                    return
                else:
                    raise IncorrectDataType(name[arg.index(a)], supstr, a)
        else:
            if not isinstance(arg, sup):
                raise IncorrectDataType(name, supstr, arg)
