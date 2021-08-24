from asyncio import TimeoutError
from time import time
from typing import List, Optional, Union

from discord import Embed, Emoji, Member, PartialEmoji, Role, TextChannel, User
from discord.abc import User as userUser
from discord.ext import commands
from discord.role import Role as roleRole
from discord_slash import SlashContext
from discord_slash.context import ComponentContext, MenuContext
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
    BadContent,
    BadEmoji,
    BadOnly,
    IncorrectDataType,
    TooManyButtons,
)


class Paginator:
    def __init__(
        self,
        bot: commands.Bot,
        ctx: Union[
            SlashContext,
            commands.Context,
            ComponentContext,
            MenuContext,
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
        timeout: Optional[int] = None,
        disableAfterTimeout: Optional[bool] = True,
        deleteAfterTimeout: Optional[bool] = False,
        useSelect: Optional[bool] = True,
        useButtons: Optional[bool] = True,
        useIndexButton: Optional[bool] = None,
        useLinkButton: Optional[bool] = False,
        useFirstLast: Optional[bool] = True,
        firstLabel: Optional[str] = "",
        prevLabel: Optional[str] = "",
        indexLabel: Optional[str] = "Page",
        nextLabel: Optional[str] = "",
        lastLabel: Optional[str] = "",
        linkLabel: Optional[Union[str, List[str]]] = "",
        linkURL: Optional[Union[str, List[str]]] = "",
        customButtonLabel: Optional[str] = None,
        firstEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "⏮️",
        prevEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "◀",
        nextEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "▶",
        lastEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = "⏭️",
        customButtonEmoji: Optional[Union[Emoji, PartialEmoji, dict, str]] = None,
        firstStyle: Optional[Union[ButtonStyle, int]] = 1,
        prevStyle: Optional[Union[ButtonStyle, int]] = 1,
        indexStyle: Optional[Union[ButtonStyle, int]] = 2,
        nextStyle: Optional[Union[ButtonStyle, int]] = 1,
        lastStyle: Optional[Union[ButtonStyle, int]] = 1,
        customButtonStyle: Optional[Union[ButtonStyle, int]] = 2,
    ):
        self.bot = bot
        self.ctx = ctx
        self.pages = pages
        self.content = content
        self.hidden = hidden
        self.authorOnly = authorOnly
        self.onlyFor = onlyFor
        self.timeout = timeout
        self.disableAfterTimeout = disableAfterTimeout
        self.deleteAfterTimeout = deleteAfterTimeout
        self.useSelect = useSelect
        self.useButtons = useButtons
        self.useIndexButton = useIndexButton
        self.useLinkButton = useLinkButton
        self.useFirstLast = useFirstLast
        self.firstLabel = firstLabel
        self.prevLabel = prevLabel
        self.indexLabel = indexLabel
        self.nextLabel = nextLabel
        self.lastLabel = lastLabel
        self.linkLabel = linkLabel
        self.linkURL = linkURL
        self.customButtonLabel = customButtonLabel
        self.firstEmoji = firstEmoji
        self.prevEmoji = prevEmoji
        self.nextEmoji = nextEmoji
        self.lastEmoji = lastEmoji
        self.customButtonEmoji = customButtonEmoji
        self.firstStyle = firstStyle
        self.prevStyle = prevStyle
        self.indexStyle = indexStyle
        self.nextStyle = nextStyle
        self.lastStyle = lastStyle
        self.customButtonStyle = customButtonStyle

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

        # ERROR HANDLING

        if not isinstance(self.bot, commands.Bot):
            raise IncorrectDataType("bot", "commands.Bot", self.bot)
        if (
            not isinstance(self.ctx, SlashContext)
            and not isinstance(self.ctx, commands.Context)
            and not isinstance(self.ctx, ComponentContext)
            and not isinstance(self.ctx, MenuContext)
            and not isinstance(self.ctx, TextChannel)
            and not isinstance(self.ctx, User)
            and not isinstance(self.ctx, Member)
        ):
            raise IncorrectDataType(
                "ctx",
                "SlashContext, commands.Context, ComponentContext, MenuContext, discord.TextChannel, discord.User,"
                + " or discord.Member",
                self.ctx,
            )
        if isinstance(self.content, list):
            if len(self.content) < self.top:
                self.content = self.content[0]
                if not isinstance(self.content, str):
                    raise BadContent(self.content)
            else:
                self.content = self.content[: self.top]
                for s in self.content:
                    if not isinstance(s, str):
                        raise BadContent(self.content)
                self.multiContent = True
        elif not isinstance(self.content, str):
            if self.content is not None:
                raise BadContent(self.content)
        if not isinstance(self.hidden, bool):
            raise IncorrectDataType("hidden", "bool", self.hidden)
        if not isinstance(self.authorOnly, bool):
            raise IncorrectDataType("authorOnly", "bool", self.authorOnly)
        if not isinstance(self.onlyFor, User):
            if not isinstance(self.onlyFor, Role):
                if not isinstance(self.onlyFor, list):
                    if self.onlyFor is not None:
                        raise IncorrectDataType(
                            "onlyFor",
                            "discord.User, Role, or list of discord.User/Role",
                            self.onlyFor,
                        )
        if not isinstance(self.timeout, int):
            if self.timeout is not None:
                raise IncorrectDataType("timeout", "int", self.timeout)
        if not isinstance(self.disableAfterTimeout, bool):
            raise IncorrectDataType(
                "disableAfterTimeout", "bool", self.disableAfterTimeout
            )
        if not isinstance(self.deleteAfterTimeout, bool):
            raise IncorrectDataType(
                "deleteAfterTimeout", "bool", self.deleteAfterTimeout
            )
        if not isinstance(self.useSelect, bool):
            raise IncorrectDataType("useSelect", "bool", self.useSelect)
        if not isinstance(self.useButtons, bool):
            raise IncorrectDataType("useButtons", "bool", self.useButtons)
        if (
            not isinstance(self.useIndexButton, bool)
            and self.useIndexButton is not None
        ):
            raise IncorrectDataType("useIndexButton", "bool", self.useIndexButton)
        if not isinstance(self.useLinkButton, bool):
            raise IncorrectDataType("useLinkButton", "bool", self.useLinkButton)
        if not isinstance(self.firstLabel, str):
            raise IncorrectDataType("firstLabel", "str", self.firstLabel)
        if not isinstance(self.prevLabel, str):
            raise IncorrectDataType("prevLabel", "str", self.prevLabel)
        if not isinstance(self.nextLabel, str):
            raise IncorrectDataType("nextLabel", "str", self.nextLabel)
        if not isinstance(self.lastLabel, str):
            raise IncorrectDataType("lastLabel", "str", self.lastLabel)

        if isinstance(self.linkLabel, list):
            if len(self.linkLabel) < self.top:
                self.linkLabel = self.linkLabel[0]
                if not isinstance(self.linkLabel, str):
                    raise IncorrectDataType(
                        "linkLabel", "str or list of str", self.linkLabel
                    )
            else:
                self.linkLabel = self.linkLabel[: self.top]
                for s in self.linkLabel:
                    if not isinstance(s, str):
                        raise IncorrectDataType(
                            "linkLabel", "str or list of str", self.linkLabel
                        )
                self.multiLabel = True
        elif not isinstance(self.linkLabel, str):
            raise IncorrectDataType("linkLabel", "str or list of str", self.linkLabel)
        if isinstance(self.linkURL, list):
            if len(self.linkURL) < self.top:
                self.linkURL = self.linkURL[0]
                if not isinstance(self.linkURL, str):
                    raise IncorrectDataType(
                        "linkURL", "str or list of str", self.linkURL
                    )
            else:
                self.linkURL = self.linkURL[: self.top]
                for s in self.linkURL:
                    if not isinstance(s, str):
                        raise IncorrectDataType(
                            "linkURL", "str or list of str", self.linkURL
                        )
                self.multiURL = True
        elif not isinstance(self.linkURL, str):
            raise IncorrectDataType("linkURL", "str or list of str", self.linkURL)
        if not isinstance(self.customButtonLabel, str):
            if self.customButtonLabel is not None:
                raise IncorrectDataType(
                    "customButtonLabel", "str", self.customButtonLabel
                )
        emojis = [self.firstEmoji, self.prevEmoji, self.nextEmoji, self.lastEmoji]
        for emoji in emojis:
            num = emojis.index(emoji) + 1
            if (
                not isinstance(emoji, Emoji)
                and not isinstance(emoji, PartialEmoji)
                and not isinstance(emoji, dict)
                and not isinstance(emoji, str)
            ):
                raise BadEmoji(num)
        if not isinstance(self.indexStyle, ButtonStyle) and not isinstance(
            self.indexStyle, int
        ):
            raise IncorrectDataType("indexStyle", "ButtonStyle or int", self.indexStyle)
        if not isinstance(self.firstStyle, ButtonStyle) and not isinstance(
            self.firstStyle, int
        ):
            raise IncorrectDataType("firstStyle", "ButtonStyle or int", self.firstStyle)
        if not isinstance(self.prevStyle, ButtonStyle) and not isinstance(
            self.prevStyle, int
        ):
            raise IncorrectDataType("prevStyle", "ButtonStyle or int", self.prevStyle)
        if not isinstance(self.nextStyle, ButtonStyle) and not isinstance(
            self.nextStyle, int
        ):
            raise IncorrectDataType("nextStyle", "ButtonStyle or int", self.nextStyle)
        if not isinstance(self.lastStyle, ButtonStyle) and not isinstance(
            self.lastStyle, int
        ):
            raise IncorrectDataType("lastStyle", "ButtonStyle or int", self.lastStyle)
        if not isinstance(self.customButtonStyle, ButtonStyle) and not isinstance(
            self.customButtonStyle, int
        ):
            raise IncorrectDataType(
                "customButtonStyle", "ButtonStyle or int", self.customButtonStyle
            )
        if self.useIndexButton and not self.useButtons:
            BadButtons("Index button cannot be used with useButtons=False!")

        if self.authorOnly and self.onlyFor:
            BadOnly()
            self.authorOnly = False

        if self.customButtonLabel is not None:
            self.useCustomButton = True

        if self.useSelect and len(self.pages) > 25:
            self.useSelect = False
            if self.useIndexButton is None:
                self.useIndexButton = True

        self.index = 1

    async def run(self):
        try:
            msg = await self.ctx.send(
                content=self.content[0] if self.multiContent else self.content,
                embed=self.pages[0],
                components=self.components(),
                hidden=self.hidden,
            )
        except TypeError:
            msg = await self.ctx.send(
                content=self.content[0] if self.multiContent else self.content,
                embed=self.pages[0],
                components=self.components(),
            )
        # handling the interaction
        tmt = True  # stop listening when timeout expires
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
                if buttonContext.custom_id == "first":
                    self.index = 1
                elif buttonContext.custom_id == "prev":
                    self.index = self.index - 1 or 1
                elif buttonContext.custom_id == "next":
                    self.index = self.index + 1 or self.top
                elif buttonContext.custom_id == "last":
                    self.index = self.top
                elif buttonContext.custom_id == "select":
                    self.index = int(buttonContext.selected_options[0])

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
                lastEmbed = self.pages[self.index - 1]
                return TimedOut(
                    self.ctx,
                    buttonContext,
                    timeTaken,
                    lastEmbed,
                    self.successfulUsers,
                    self.failedUsers,
                )

    def check(self, buttonContext):
        if self.authorOnly and buttonContext.author.id != self.ctx.author.id:
            if buttonContext.author not in self.failedUsers:
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
                self.failedUsers.append(buttonContext.author)
                return False

        return True

    def components(self):
        disableLeft = self.index == 1
        disableRight = self.index == self.top
        controlButtons = [
            # Previous Button
            create_button(
                style=self.prevStyle,
                label=self.prevLabel,
                custom_id="prev",
                disabled=disableLeft,
                emoji=self.prevEmoji,
            ),
            # Index
            create_button(
                style=self.indexStyle,
                label=f"{self.indexLabel} {self.index}/{self.top}",
                disabled=True,
            ),
            # Next Button
            create_button(
                style=self.nextStyle,
                label=self.nextLabel,
                custom_id="next",
                disabled=disableRight,
                emoji=self.nextEmoji,
            ),
        ]
        if not self.useIndexButton:
            controlButtons.pop(1)
        if self.useFirstLast:
            controlButtons.insert(
                0,
                create_button(
                    style=self.firstStyle,
                    label=self.firstLabel,
                    custom_id="first",
                    disabled=disableLeft,
                    emoji=self.firstEmoji,
                ),
            )
            controlButtons.append(
                create_button(
                    style=self.lastStyle,
                    label=self.lastLabel,
                    custom_id="last",
                    disabled=disableRight,
                    emoji=self.lastEmoji,
                )
            )
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
        self.useIndexButton = False if not self.useButtons else self.useIndexButton
        if self.useLinkButton:
            linkButton = create_button(
                style=5,
                label=self.linkLabel[0] if self.multiLabel else self.linkLabel,
                url=self.linkURL[0] if self.multiURL else self.linkURL,
            )
            if len(controlButtons) < 5:
                controlButtons.append(linkButton)
            else:
                raise TooManyButtons()
        if self.useCustomButton:
            customButton = create_button(
                style=self.customButtonStyle,
                label=self.customButtonLabel,
                disabled=True,
                emoji=self.customButtonEmoji,
            )
            if len(controlButtons) < 5:
                controlButtons.append(customButton)
            else:
                raise TooManyButtons()
        buttonControls = create_actionrow(*controlButtons)
        components = []
        if self.useSelect:
            select = create_select(
                options=select_options,
                custom_id="select",
                placeholder=f"{self.indexLabel} {self.index}/{self.top}",
                min_values=1,
                max_values=1,
            )
            selectControls = create_actionrow(select)
            components.append(selectControls)
        if self.useButtons:
            components.append(buttonControls)
        return components


class TimedOut:
    def __init__(
        self, ctx, buttonContext, timeTaken, lastEmbed, successfulUsers, failedUsers
    ):
        self.ctx = ctx
        self.buttonContext = buttonContext
        self.timeTaken = timeTaken
        self.lastEmbed = lastEmbed
        self.successfulUsers = successfulUsers
        self.failedUsers = failedUsers
