from asyncio import get_running_loop, sleep
from random import randint
from time import perf_counter
from typing import List, Optional, Union, Coroutine

from interactions import (
    Embed,
    Emoji,
    Member,
    Message,
    Role,
    User,
    Attachment,
    Channel,
    ButtonStyle,
)
from interactions import Client
from interactions.context import InteractionContext, Context, ComponentContext
from interactions.api.error import HTTPException
from interactions.models.component import (
    ActionRow,
    Button,
    SelectMenu,
    SelectOption,
)

from .errors import BadButtons, BadOnly, IncorrectDataType, TooManyButtons, TooManyFiles


class TimedOut:
    def __init__(
        self,
        ctx: Union[
            InteractionContext,
            Context,
            Channel,
            User,
            Member,
        ],
        buttonContext: Union[ComponentContext, type(None)],
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
        bot: Client,
        ctx: Union[
            InteractionContext,
            Context,
            Channel,
            User,
            Member,
        ],
        pages: Optional[List[Embed]] = None,
        content: Optional[Union[str, List[str]]] = None,
        editOnMessage: Optional[Message] = False,
        files: Optional[Union[Attachment, List[Attachment]]] = None,
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
        customButton: Optional[
            List[Union[Union[Button, SelectMenu], Coroutine]]
        ] = None,
        customActionRow: Optional[
            List[Union[Union[Button, SelectMenu], Coroutine]]
        ] = None,
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
        firstEmoji: Optional[Union[Emoji, dict, str]] = "⏮️",
        prevEmoji: Optional[Union[Emoji, dict, str]] = "◀",
        nextEmoji: Optional[Union[Emoji, dict, str]] = "▶",
        lastEmoji: Optional[Union[Emoji, dict, str]] = "⏭️",
        quitButtonEmoji: Optional[Union[Emoji, dict, str]] = None,
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
        self.timedOut = False
        self.buttonContext = None
        self.msg = None
        self.start = None
        self.id = randint(1, 999999)

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
            if isinstance(self.ctx, (InteractionContext, Context, ComponentContext)):
                self.msg = await self.ctx.author.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embeds=self.pages[0],
                    components=self.components(),
                )
                await self.ctx.send("Check your DMs!", ephemeral=True) if isinstance(
                    self.ctx, InteractionContext
                ) else await self.ctx.send("Check your DMs!")
            elif isinstance(self.ctx, User):
                self.msg = await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embeds=self.pages[0],
                    components=self.components(),
                )
            else:
                raise IncorrectDataType(
                    "ctx",
                    "InteractionContext, Context, ComponentContext, or user for dm=True",
                    self.ctx,
                )
        elif self.editOnMessage:
            await self.editOnMessage.edit(
                content=self.content[0] if self.multiContent else self.content,
                embeds=self.pages[0],
                components=self.components(),
            )
            self.msg = self.editOnMessage
        else:
            self.msg = (
                await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embeds=self.pages[0],
                    components=self.components(),
                    ephemeral=self.hidden,
                )
                if isinstance(self.ctx, InteractionContext)
                else await self.ctx.send(
                    content=self.content[0] if self.multiContent else self.content,
                    embeds=self.pages[0],
                    components=self.components(),
                )
            )
        for component in ["first", "prev", "next", "last"]:
            self.bot.websocket.dispatch.register(self.componentCallback, name=component)
        # more useful variables:
        self.start = perf_counter()
        timer = self.timeout
        # loop:
        while True:
            if self.timedOut:
                timer = 0
                break
            if timer <= 0:
                self.timedOut = True
                break
            if self.stop:  # if self.stop == True
                # what to do after timeout:
                try:
                    if self.deleteAfterTimeout and not self.hidden:
                        await self.msg.edit(components=None)
                    elif self.disableAfterTimeout and not self.hidden:
                        await self.msg.edit(components=self.disabled())
                except HTTPException:
                    pass
                # returns useful data:
                return TimedOut(
                    self.ctx,
                    self.buttonContext,
                    round(perf_counter() - self.start),
                    self.content
                    if isinstance(self.content, (str, type(None)))
                    else self.content[self.index - 1],
                    self.pages[self.index - 1] if self.embeds else None,
                    self.successfulUsers,
                    self.failedUsers,
                )
            timer -= 1
            await sleep(1)
        return TimedOut(
            self.ctx,
            self.buttonContext,
            round(perf_counter() - self.start),
            self.content
            if isinstance(self.content, (str, type(None)))
            else self.content[self.index - 1],
            self.pages[self.index - 1] if self.embeds else None,
            self.successfulUsers,
            self.failedUsers,
        )

    # component callback:
    async def componentCallback(self, buttonContext: ComponentContext):
        self.buttonContext = buttonContext
        customID = buttonContext.custom_id
        if self.timedOut:
            return
        elif self.stop:
            return
        elif buttonContext.message.id != self.msg.id:
            return
        elif not self.check(buttonContext):
            return
        if customID == f"first{self.id}":
            self.index = 1
        elif customID == f"prev{self.id}":
            self.index -= 1
        elif customID == f"next{self.id}":
            self.index += 1
        elif customID == f"last{self.id}":
            self.index = len(self.pages)
        elif customID == f"select{self.id}":
            self.index = int(buttonContext.values[0])
        elif customID == f"quit{self.id}":
            end = perf_counter()
            try:
                if not self.timeoutEmbed:
                    if self.deleteAfterTimeout and not self.hidden:
                        await buttonContext.edit_origin(components=None)
                    elif self.disableAfterTimeout and not self.hidden:
                        await buttonContext.edit_origin(components=self.disabled())
                else:
                    if self.deleteAfterTimeout and not self.hidden:
                        await buttonContext.edit_origin(
                            components=None, embed=self.timeoutEmbed
                        )
                    elif self.disableAfterTimeout and not self.hidden:
                        await buttonContext.edit_origin(
                            components=self.disabled(), embed=self.timeoutEmbed
                        )
            except HTTPException:
                pass
            if not buttonContext.responded:
                await buttonContext.defer(ignore=True)
            timeTaken = round(end - self.start)
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
        elif buttonContext.custom_id == f"customButton{self.id}":
            if self.customButton is not None:
                await self.customButton[1](self, buttonContext)
            if not buttonContext.responded:
                await buttonContext.defer(ignore=True)
            return
            # uses the customActionRow
        elif self.customActionRow is not None:
            await self.customActionRow[1](self, buttonContext)
            if not buttonContext.responded:
                await buttonContext.defer(ignore=True)
            return
            # finally edits based on changed values
        await buttonContext.edit_origin(
            content=self.content[self.index - 1] if self.multiContent else self.content,
            embed=self.pages[self.index - 1] if self.embeds else None,
            components=self.components(),
        )

    # check for wait_for_component() in self.run()
    def check(self, buttonContext: ComponentContext) -> bool:
        # if authorOnly and not same author:
        if self.authorOnly and buttonContext.author.id != self.ctx.author.id:
            if self.useNotYours:  # whether or not to send hidden message
                get_running_loop().create_task(
                    buttonContext.send(
                        f"{buttonContext.author.mention}, {self.notYoursMessage}",
                        ephemeral=True,
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
                for user in filter(lambda x: isinstance(x, User), self.onlyFor):
                    check = check or user.id == buttonContext.author.id
                # checks if user has role in onlyFor:
                for role in filter(lambda x: isinstance(x, Role), self.onlyFor):
                    check = check or role in buttonContext.author.roles
            else:
                # checks if user in onlyFor:
                if isinstance(self.onlyFor, User):
                    check = check or self.onlyFor.id == buttonContext.author.id
                # checks if user has role in onlyFor:
                elif isinstance(self.onlyFor, Role):
                    check = check or self.onlyFor in buttonContext.author.roles

            if not check:  # if check is False:
                if self.useNotYours:
                    get_running_loop().create_task(
                        buttonContext.send(
                            f"{buttonContext.author.mention}, {self.notYoursMessage}",
                            ephemeral=True,
                        )
                    )
                if buttonContext.author not in self.failedUsers:
                    self.failedUsers.append(buttonContext.author)
                return False
        return True

    # select:
    def select_row(self) -> ActionRow:
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
                        SelectOption(
                            label=f"{pageNum}: Title not found", value=f"{pageNum}"
                        )
                    )
                else:  # if there is a title:
                    # makes sure that title is 100 characters or less
                    title = (title[:93] + "...") if len(title) > 96 else title
                    select_options.append(
                        SelectOption(label=f"{pageNum}: {title}", value=f"{pageNum}")
                    )
            except Exception:  # if it failed for some reason:
                select_options.append(
                    SelectOption(
                        label=f"{pageNum}: Title not found", value=f"{pageNum}"
                    )
                )
        select = SelectMenu(
            options=select_options,
            custom_id="select",
            placeholder=f"{self.labels[2]} {self.index}/{self.top}",  # shows the index
            min_values=1,
            max_values=1,
        )
        return ActionRow(components=select)

    # buttons:
    def buttons_row(self) -> ActionRow:
        disableLeft = self.index == 1  # if buttons on left should be disabled
        disableRight = self.index == self.top  # if buttons on right should be disabled
        controlButtons = [
            Button(  # previous button
                style=self.styles[1],
                label=self.labels[1],
                custom_id=f"prev{self.id}",
                disabled=disableLeft,
                emoji=self.emojis[1],
            ),
            Button(  # index button
                style=self.styles[2],
                label=f"{self.labels[2]} {self.index}/{self.top}",
                disabled=True,
            ),
            Button(  # next button
                style=self.styles[3],
                label=self.labels[3],
                custom_id=f"next{self.id}",
                disabled=disableRight,
                emoji=self.emojis[2],
            ),
        ]
        # removes index button if not useIndexButton:
        controlButtons.pop(1) if not self.useIndexButton else None
        if self.useFirstLast:
            controlButtons.insert(
                0,
                Button(  # first page button
                    style=self.styles[0],
                    label=self.labels[0],
                    custom_id=f"first{self.id}",
                    disabled=disableLeft,
                    emoji=self.emojis[0],
                ),
            )
            controlButtons.append(
                Button(  # last page button
                    style=self.styles[4],
                    label=self.labels[4],
                    custom_id=f"last{self.id}",
                    disabled=disableRight,
                    emoji=self.emojis[3],
                )
            )
        if self.useLinkButton:
            linkButton = Button(  # link button
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
            if customButton.custom_id != f"customButton{self.id}":
                customButton.custom_id = f"customButton{self.id}"
            # appends the button only if there is space in the action row:
            if len(controlButtons) < 5:
                controlButtons.append(customButton)
                self.usedCustom = True
            elif not self.useOverflow:
                raise TooManyButtons()
        if self.useQuitButton:
            quitButton = Button(  # quit button
                style=self.quit[0],
                label=self.quit[1],
                emoji=self.quit[2],
                custom_id=f"quit{self.id}",
            )
            # appends the button only if there is space in the action row:
            if len(controlButtons) < 5:
                controlButtons.append(quitButton)
                self.usedQuit = True
            elif not self.useOverflow:
                raise TooManyButtons()
        return ActionRow(components=controlButtons)

    # overflow row:
    def overflow_row(self) -> ActionRow:
        controlButtons = []
        # checks if button is not already in self.buttons():
        if self.useLinkButton and not self.usedLink:
            linkButton = Button(  # link button
                style=5,
                label=self.links[0][0] if self.multiLabel else self.links[0],
                url=self.links[1][0] if self.multiURL else self.links[1],
            )
            controlButtons.append(linkButton) if len(controlButtons) < 5 else None
        # checks if button is not already in self.buttons():
        if self.useCustomButton and not self.usedCustom:
            customButton = self.customButton[0]  # custom button
            if customButton.custom_id != f"customButton{self.id}":
                customButton.custom_id = f"customButton{self.id}"
            controlButtons.append(customButton) if len(controlButtons) < 5 else None
        # checks if button is not already in self.buttons():
        if self.useQuitButton and not self.usedQuit:
            quitButton = Button(  # quit button
                style=self.quit[0],
                label=self.quit[1],
                emoji=self.quit[2],
                custom_id="quit",
            )
            controlButtons.append(quitButton) if len(controlButtons) < 5 else None
        return None if controlButtons == [] else ActionRow(components=controlButtons)

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

    # disabled components:
    def disabled(self) -> list:
        components = self.components()
        for row in components:
            for component in row.components:
                component.disabled = True
        return components

    # lets you go to a specific page:
    def goToPage(self, page: int) -> None:
        if page < 1:
            page = 1
        elif page > self.top:
            page = self.top
        self.index = page
