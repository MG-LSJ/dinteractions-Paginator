from asyncio import TimeoutError, get_running_loop
from time import perf_counter
from typing import List, Optional, Union, Awaitable

from discord import Embed, Emoji, Member, Message, PartialEmoji, Role, User, File
from discord.abc import User as userUser
from discord.channel import TextChannel
from discord.ext.commands import AutoShardedBot, Bot, Context
from discord.errors import NotFound
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

from .errors import BadButtons, BadOnly, IncorrectDataType, TooManyButtons, TooManyFiles


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
        lastEmbed: Union[Embed, type(None)],
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
        pages: Optional[List[Embed]] = None,
        content: Optional[Union[str, List[str]]] = None,
        editOnMessage: Optional[Message] = False,
        files: Optional[Union[File, List[File]]] = None,
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
        customButton: Optional[List[Union[dict, Awaitable]]] = None,
        customActionRow: Optional[List[Union[dict, Awaitable]]] = None,
        timeout: Optional[int] = None,
        disableAfterTimeout: Optional[bool] = True,
        deleteAfterTimeout: Optional[bool] = False,
        timeoutEmbed: Optional[Embed] = None,
        useEmoji: Optional[bool] = True,
        useSelect: Optional[bool] = True,
        useButtons: Optional[bool] = True,
        useIndexButton: Optional[bool] = None,
        useLinkButton: Optional[bool] = False,
        useQuitButton: Optional[bool] = False,
        useFirstLast: Optional[bool] = True,
        useOverflow: Optional[bool] = True,
        useNotYours: Optional[bool] = True,
        notYoursMessage: Optional[str] = "this paginator is not for you!",
        firstLabel: Optional[str] = "",
        prevLabel: Optional[str] = "",
        indexLabel: Optional[str] = "Page",
        nextLabel: Optional[str] = "",
        lastLabel: Optional[str] = "",
        linkLabel: Optional[Union[str, List[str]]] = "",
        linkURL: Optional[Union[str, List[str]]] = "",
        quitButtonLabel: Optional[str] = "Quit",
        firstEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "⏮️",
        prevEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "◀",
        nextEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "▶",
        lastEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "⏭️",
        quitButtonEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = None,
        firstStyle: Optional[Union[ButtonStyle, int]] = 1,
        prevStyle: Optional[Union[ButtonStyle, int]] = 1,
        indexStyle: Optional[Union[ButtonStyle, int]] = 2,
        nextStyle: Optional[Union[ButtonStyle, int]] = 1,
        lastStyle: Optional[Union[ButtonStyle, int]] = 1,
        quitButtonStyle: Optional[Union[ButtonStyle, int]] = 4,
    ) -> None:
        # attributes:
        self.bot = bot
        self.ctx = ctx
        self.pages = [pages] if isinstance(pages, type(None)) else pages
        self.content = content
        self.editOnMessage = editOnMessage
        self.files = files if isinstance(files, (list, type(None))) else [files]
        self.hidden = hidden
        self.authorOnly = authorOnly
        self.onlyFor = onlyFor
        self.dm = dm
        self.timeout = timeout
        self.disableAfterTimeout = disableAfterTimeout
        self.deleteAfterTimeout = deleteAfterTimeout
        self.timeoutEmbed = timeoutEmbed
        self.useEmoji = useEmoji
        self.useSelect = useSelect
        self.useButtons = useButtons
        self.useIndexButton = useIndexButton
        self.useLinkButton = useLinkButton
        self.useQuitButton = useQuitButton
        self.useFirstLast = useFirstLast
        self.useOverflow = useOverflow
        self.useNotYours = useNotYours
        self.notYoursMessage = notYoursMessage
        self.labels = [firstLabel, prevLabel, indexLabel, nextLabel, lastLabel]
        self.links = [linkLabel, linkURL]
        self.quit = [
            quitButtonStyle,
            quitButtonLabel,
            quitButtonEmoji if useEmoji else None,
        ]
        self.emojis = (
            [firstEmoji, prevEmoji, nextEmoji, lastEmoji]
            if useEmoji
            else [None, None, None, None]
        )
        self.styles = [firstStyle, prevStyle, indexStyle, nextStyle, lastStyle]
        self.customButton = customButton
        self.customActionRow = customActionRow

        if self.pages is None and not isinstance(self.content, list):
            raise IncorrectDataType(
                "both pages and content",
                "content has to be a list of strings if pages is not used!",
                self.pages,
            )

        # useful variables:
        self.embeds = self.pages[0] is not None
        self.top = len(self.pages) if self.embeds else len(self.content)
        self.useCustomButton = False
        self.multiLabel = self.multiContent = self.multiURL = False
        try:
            self.successfulUsers = [ctx.author]
        except AttributeError:
            self.successfulUsers = [ctx]
        self.failedUsers = []
        self.usedLink = self.usedCustom = self.usedQuit = False
        self.index = 1
        self.stop = False

        # error handling:
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
        self.incdata("pages", self.pages, list, "List[discord.Embed]")
        self.incdata(
            "content", self.content, (list, str, type(None)), "str or list(str)"
        )
        self.incdata(
            "editOnMessage",
            self.editOnMessage,
            (Message, type(None)),
            "discord.Message",
        )
        self.incdata("files", self.files, (list, type(None)), "List[discord.File]")
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
            "useEmoji": self.useEmoji,
            "useSelect": self.useSelect,
            "useButtons": self.useButtons,
            "useLinkButton": self.useLinkButton,
            "useQuitButton": self.useQuitButton,
            "useFirstLast": self.useFirstLast,
            "useOverflow": self.useOverflow,
            "useNotYours": self.useNotYours,
        }
        self.incdata(
            bools,
            None,
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
        self.incdata(
            labels,
            None,
            str,
            "str",
        )
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
        self.incdata(
            emojis,
            None,
            (Emoji, PartialEmoji, dict, str, type(None)),
            "Emoji, PartialEmoji, dict, str, or None",
        )
        styles = {
            "firstStyle": firstStyle,
            "prevStyle": prevStyle,
            "indexStyle": indexStyle,
            "nextStyle": nextStyle,
            "lastStyle": lastStyle,
            "quitButtonStyle": quitButtonStyle,
        }
        self.incdata(
            styles,
            None,
            (ButtonStyle, int),
            "ButtonStyle or int",
        )
        self.incdata(
            "customButton",
            self.customButton,
            (list, type(None)),
            "a list with create_button(...), then the awaitable function",
        )
        self.incdata(
            "customActionRow",
            self.customActionRow,
            (list, type(None)),
            "a list with the action row, then the awaitable function",
        )
        self.incdata(
            "notYoursMessage",
            self.notYoursMessage,
            (str, type(None)),
            "str",
        )
        self.incdata(
            "timeoutEmbed",
            self.timeoutEmbed,
            (Embed, type(None)),
            "discord.Embed",
        )
        self.multiContent = type(self.content) == list
        self.multiLabel = type(self.links[0]) == list
        self.multiURL = type(self.links[1]) == list
        if self.useIndexButton and not self.useButtons:
            BadButtons("Index button cannot be used with useButtons=False!")
            self.useIndexButton = False
        if self.authorOnly and self.onlyFor:
            BadOnly()
            self.authorOnly = False
        if self.customButton is not None:
            self.useCustomButton = True
        if self.useSelect and len(self.pages) > 25:
            self.useSelect = False
            if self.useIndexButton is None:
                self.useIndexButton = True
        if isinstance(self.files, list):
            if len(self.files) > 10:
                raise TooManyFiles

    # main:
    async def run(self) -> TimedOut:
        # sending the message based on context and dm:
        if self.dm:
            if isinstance(self.ctx, (InteractionContext, Context)):
                msg = await self.ctx.author.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embed=self.pages[0],
                    components=self.components(),
                    files=self.files,
                )
                await self.ctx.send("Check your DMs!", hidden=True) if isinstance(
                    self.ctx, InteractionContext
                ) else await self.ctx.send("Check your DMs!")
            elif isinstance(self.ctx, userUser):
                msg = await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embed=self.pages[0],
                    components=self.components(),
                    files=self.files,
                )
            else:
                raise IncorrectDataType(
                    "ctx",
                    "InteractionContext, commands.Context, or user for dm=True",
                    self.ctx,
                )
        elif self.editOnMessage:
            await self.editOnMessage.edit(
                content=self.content[0] if self.multiContent else self.content,
                embed=self.pages[0],
                components=self.components(),
            )
            msg = self.editOnMessage
        else:
            msg = (
                await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embed=self.pages[0],
                    components=self.components(),
                    hidden=self.hidden,
                    files=self.files,
                )
                if isinstance(self.ctx, InteractionContext)
                else await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embed=self.pages[0],
                    components=self.components(),
                    files=self.files,
                )
            )
        # more useful variables:
        start = perf_counter()
        buttonContext = None
        # loop:
        while True:
            if self.stop:  # if self.stop == True
                # what to do after timeout:
                try:
                    if self.deleteAfterTimeout and not self.hidden:
                        await msg.edit(components=None)
                    elif self.disableAfterTimeout and not self.hidden:
                        await msg.edit(components=self.disabled())
                except NotFound:
                    pass
                # returns useful data:
                return TimedOut(
                    self.ctx,
                    buttonContext,
                    round(perf_counter() - start),
                    self.content
                    if isinstance(self.content, (str, type(None)))
                    else self.content[self.index - 1],
                    self.pages[self.index - 1] if self.embeds else None,
                    self.successfulUsers,
                    self.failedUsers,
                )
            try:  # to catch TimeoutError if timeout
                buttonContext: ComponentContext = await wait_for_component(
                    self.bot,
                    messages=msg,
                    check=self.check,
                    components=self.components(),
                    timeout=self.timeout,
                )  # waits for any component in the message
                # add person who used it to the list:
                if buttonContext.author not in self.successfulUsers:
                    self.successfulUsers.append(buttonContext.author)
                # custom_id checks to determine which component:
                if buttonContext.custom_id == "first":
                    self.index = 1
                elif buttonContext.custom_id == "prev":
                    self.index = self.index - 1 or 1
                elif buttonContext.custom_id == "next":
                    self.index = self.index + 1 or self.top
                elif buttonContext.custom_id == "last":
                    self.index = self.top
                # select:
                elif buttonContext.custom_id == "select":
                    self.index = int(buttonContext.selected_options[0])
                # quit button:
                elif buttonContext.custom_id == "quit":
                    end = perf_counter()
                    try:
                        if not self.timeoutEmbed:
                            if self.deleteAfterTimeout and not self.hidden:
                                await buttonContext.edit_origin(components=None)
                            elif self.disableAfterTimeout and not self.hidden:
                                await buttonContext.edit_origin(
                                    components=self.disabled()
                                )
                        else:
                            if self.deleteAfterTimeout and not self.hidden:
                                await buttonContext.edit_origin(
                                    components=None, embed=self.timeoutEmbed
                                )
                            elif self.disableAfterTimeout and not self.hidden:
                                await buttonContext.edit_origin(
                                    components=self.disabled(), embed=self.timeoutEmbed
                                )
                    except NotFound:
                        pass
                    if not buttonContext.responded:
                        await buttonContext.defer(ignore=True)
                    timeTaken = round(end - start)
                    lastContent = (
                        self.content
                        if isinstance(self.content, (str, type(None)))
                        else self.content[self.index - 1]
                    )
                    lastEmbed = self.pages[self.index - 1] if self.embeds else None
                    return TimedOut(
                        self.ctx,
                        buttonContext,
                        timeTaken,
                        lastContent,
                        lastEmbed,
                        self.successfulUsers,
                        self.failedUsers,
                    )
                # customButton:
                elif buttonContext.custom_id == "customButton":
                    if self.customButton is not None:
                        await self.customButton[1](self, buttonContext)
                    if not buttonContext.responded:
                        await buttonContext.defer(ignore=True)
                    continue
                # uses the customActionRow
                elif self.customActionRow is not None:
                    await self.customActionRow[1](self, buttonContext)
                    if not buttonContext.responded:
                        await buttonContext.defer(ignore=True)
                    continue
                # finally edits based on changed values
                await buttonContext.edit_origin(
                    content=self.content[self.index - 1]
                    if self.multiContent
                    else self.content,
                    embed=self.pages[self.index - 1] if self.embeds else None,
                    components=self.components(),
                )
            except TimeoutError:  # TimeoutError is caught due to timeout
                # what to do after timeout:
                try:
                    if not self.timeoutEmbed:
                        if self.deleteAfterTimeout and not self.hidden:
                            await msg.edit(components=None)
                        elif self.disableAfterTimeout and not self.hidden:
                            await msg.edit(components=self.disabled())
                    else:
                        if self.deleteAfterTimeout and not self.hidden:
                            await msg.edit(components=None, embed=self.timeoutEmbed)
                        elif self.disableAfterTimeout and not self.hidden:
                            await msg.edit(
                                components=self.disabled(), embed=self.timeoutEmbed
                            )
                except NotFound:
                    pass
                # returns useful data:
                return TimedOut(
                    self.ctx,
                    buttonContext,
                    round(perf_counter() - start),
                    self.content
                    if isinstance(self.content, (str, type(None)))
                    else self.content[self.index - 1],
                    self.pages[self.index - 1] if self.embeds else None,
                    self.successfulUsers,
                    self.failedUsers,
                )

    # check for wait_for_component() in self.run()
    def check(self, buttonContext: ComponentContext) -> bool:
        # if authorOnly and not same author:
        if self.authorOnly and buttonContext.author.id != self.ctx.author.id:
            if self.useNotYours:  # whether or not to send hidden message
                get_running_loop().create_task(
                    buttonContext.send(
                        f"{buttonContext.author.mention}, {self.notYoursMessage}",
                        hidden=True,
                    )
                )
            # adds author to failedUsers
            if buttonContext.author not in self.failedUsers:
                self.failedUsers.append(buttonContext.author)
            return False

        # if onlyFor is used:
        if self.onlyFor is not None:
            check = False
            if isinstance(self.onlyFor, list):
                # checks if user in onlyFor:
                for user in filter(lambda x: isinstance(x, userUser), self.onlyFor):
                    check = check or user.id == buttonContext.author.id
                # checks if user has role in onlyFor:
                for role in filter(lambda x: isinstance(x, roleRole), self.onlyFor):
                    check = check or role in buttonContext.author.roles
            else:
                # checks if user in onlyFor:
                if isinstance(self.onlyFor, userUser):
                    check = check or self.onlyFor.id == buttonContext.author.id
                # checks if user has role in onlyFor:
                elif isinstance(self.onlyFor, roleRole):
                    check = check or self.onlyFor in buttonContext.author.roles

            if not check:  # if check is False:
                if self.useNotYours:
                    get_running_loop().create_task(
                        buttonContext.send(
                            f"{buttonContext.author.mention}, {self.notYoursMessage}",
                            hidden=True,
                        )
                    )
                if buttonContext.author not in self.failedUsers:
                    self.failedUsers.append(buttonContext.author)
                return False
        return True

    # select:
    def select_row(self) -> dict:
        select_options = []
        for i in (
            self.pages if self.embeds else self.content
        ):  # loops through pages (embeds)
            pageNum = (self.pages if self.embeds else self.content).index(
                i
            ) + 1  # page number
            try:
                title = i.title if self.embeds else i  # title of embed
                if title == Embed.Empty:  # if there is no title:
                    select_options.append(
                        create_select_option(
                            f"{pageNum}: Title not found", value=f"{pageNum}"
                        )
                    )
                else:  # if there is a title:
                    # makes sure that title is 100 characters or less
                    title = (title[:93] + "...") if len(title) > 96 else title
                    select_options.append(
                        create_select_option(f"{pageNum}: {title}", value=f"{pageNum}")
                    )
            except Exception:  # if it failed for some reason:
                select_options.append(
                    create_select_option(
                        f"{pageNum}: Title not found", value=f"{pageNum}"
                    )
                )
        select = create_select(
            options=select_options,
            custom_id="select",
            placeholder=f"{self.labels[2]} {self.index}/{self.top}",  # shows the index
            min_values=1,
            max_values=1,
        )
        return create_actionrow(select)

    # buttons:
    def buttons_row(self) -> dict:
        disableLeft = self.index == 1  # if buttons on left should be disabled
        disableRight = self.index == self.top  # if buttons on right should be disabled
        controlButtons = [
            create_button(  # previous button
                style=self.styles[1],
                label=self.labels[1],
                custom_id="prev",
                disabled=disableLeft,
                emoji=self.emojis[1],
            ),
            create_button(  # index button
                style=self.styles[2],
                label=f"{self.labels[2]} {self.index}/{self.top}",
                disabled=True,
            ),
            create_button(  # next button
                style=self.styles[3],
                label=self.labels[3],
                custom_id="next",
                disabled=disableRight,
                emoji=self.emojis[2],
            ),
        ]
        # removes index button if not useIndexButton:
        controlButtons.pop(1) if not self.useIndexButton else None
        if self.useFirstLast:
            controlButtons.insert(
                0,
                create_button(  # first page button
                    style=self.styles[0],
                    label=self.labels[0],
                    custom_id="first",
                    disabled=disableLeft,
                    emoji=self.emojis[0],
                ),
            )
            controlButtons.append(
                create_button(  # last page button
                    style=self.styles[4],
                    label=self.labels[4],
                    custom_id="last",
                    disabled=disableRight,
                    emoji=self.emojis[3],
                )
            )
        if self.useLinkButton:
            linkButton = create_button(  # link button
                style=5,
                label=self.links[0][0] if self.multiLabel else self.links[0],
                url=self.links[1][0] if self.multiURL else self.links[1],
            )
            # appends the button only if there is space in the action row:
            if len(controlButtons) < 5:
                controlButtons.append(linkButton)
                self.usedLink = True
            elif not self.useOverflow:
                raise TooManyButtons()
        if self.useCustomButton:
            customButton = self.customButton[0]  # custom button
            if customButton["custom_id"] != "customButton":
                customButton["custom_id"] = "customButton"
            # appends the button only if there is space in the action row:
            if len(controlButtons) < 5:
                controlButtons.append(customButton)
                self.usedCustom = True
            elif not self.useOverflow:
                raise TooManyButtons()
        if self.useQuitButton:
            quitButton = create_button(  # quit button
                style=self.quit[0],
                label=self.quit[1],
                emoji=self.quit[2],
                custom_id="quit",
            )
            # appends the button only if there is space in the action row:
            if len(controlButtons) < 5:
                controlButtons.append(quitButton)
                self.usedQuit = True
            elif not self.useOverflow:
                raise TooManyButtons()
        return create_actionrow(*controlButtons)

    # overflow row:
    def overflow_row(self) -> dict:
        controlButtons = []
        # checks if button is not already in self.buttons():
        if self.useLinkButton and not self.usedLink:
            linkButton = create_button(  # link button
                style=5,
                label=self.links[0][0] if self.multiLabel else self.links[0],
                url=self.links[1][0] if self.multiURL else self.links[1],
            )
            controlButtons.append(linkButton) if len(controlButtons) < 5 else None
        # checks if button is not already in self.buttons():
        if self.useCustomButton and not self.usedCustom:
            customButton = self.customButton[0]  # custom button
            if customButton["custom_id"] != "customButton":
                customButton["custom_id"] = "customButton"
            controlButtons.append(customButton) if len(controlButtons) < 5 else None
        # checks if button is not already in self.buttons():
        if self.useQuitButton and not self.usedQuit:
            quitButton = create_button(  # quit button
                style=self.quit[0],
                label=self.quit[1],
                emoji=self.quit[2],
                custom_id="quit",
            )
            controlButtons.append(quitButton) if len(controlButtons) < 5 else None
        return None if controlButtons == [] else create_actionrow(*controlButtons)

    # components:
    def components(self) -> list:
        # takes the action rows from all the functions and returns as a list:
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

    # stands for incorrect data (uses indincdata)
    def incdata(self, name, arg, sup, supstr) -> None:
        # stands for individual incdata (raises IncorrectDataType)
        def indincdata(name, arg, sup, supstr):
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

        # checks if there are multiple args to be indincdata'ed:
        if isinstance(name, dict) and arg is None:
            for n in name:
                indincdata(n, name[n], sup, supstr)
        else:
            indincdata(name, arg, sup, supstr)

    # disabled components:
    def disabled(self) -> list:
        components = self.components()
        for row in components:
            for component in row["components"]:
                component["disabled"] = True
        return components

    # lets you go to a specific page:
    def goToPage(self, page: int) -> None:
        if page < 1:
            page = 1
        elif page > self.top:
            page = self.top
        self.index = page
