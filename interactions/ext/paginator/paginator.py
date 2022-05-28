from asyncio import TimeoutError
from enum import Enum
from inspect import iscoroutinefunction
from random import randint
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.ext.wait_for import setup, wait_for_component

from interactions import (
    MISSING,
    ActionRow,
    Button,
    Client,
    CommandContext,
    ComponentContext,
    Embed,
    Emoji,
    Message,
    SelectMenu,
    SelectOption,
    Snowflake,
)

from .errors import PaginatorWontWork, StopPaginator


class ButtonKind(str, Enum):
    """
    Enum for button types.

    Enums:

    - `FIRST: "first"`
    - `PREVIOUS: "prev"`
    - `INDEX: "index"`
    - `NEXT: "next"`
    - `LAST: "last"`
    """

    FIRST = "first"
    PREVIOUS = "prev"
    INDEX = "index"
    NEXT = "next"
    LAST = "last"


class DictSerializerMixin:
    __slots__ = ("_json",)

    def __init__(self, **kwargs):
        self._json = kwargs

        for key, value in kwargs.items():
            if not hasattr(self, "__slots__") or key in self.__slots__:
                setattr(self, key, value)

        if hasattr(self, "__slots__"):
            for _attr in self.__slots__:
                if not hasattr(self, _attr):
                    setattr(self, _attr, None)


class Data(DictSerializerMixin):
    """
    Data that is returned once the paginator times out.

    Attrinutes:

    - `paginator: Paginator`: The paginator that timed out.
    - `original_ctx: CommandContext | ComponentContext`: The original context.
    - `component_ctx: ComponentContext`: The context of the component.
    - `message: Message`: The message that was sent.
    """

    __slots__ = ("_json", "paginator", "original_ctx", "component_ctx", "message")
    _json: Dict[str, Any]
    paginator: "Paginator"
    original_ctx: Union[CommandContext, ComponentContext]
    component_ctx: ComponentContext
    message: Message

    def __repr__(self) -> str:
        return f"<Data paginator={self.paginator}, original_ctx={self.original_ctx}, component_ctx={self.component_ctx}, message={self.message}>"

    __str__ = __repr__


class Page(DictSerializerMixin):
    """
    An individual page to be supplied as a list of these pages to the paginator.

    Parameters:

    - `?content: str`: The content of the page.
    - `?embeds: Embed | list[Embed]`: The embeds of the page.
    - `?title: str`: The title of the page displayed in the select menu.
        - Defaults to content or the title of the embed with an available title.
    """

    __slots__ = ("_json", "content", "embeds", "title")

    def __init__(
        self,
        content: Optional[str] = None,
        embeds: Optional[Union[Embed, List[Embed]]] = None,
        title: Optional[str] = None,
    ) -> None:
        if title:
            self.title = title
        elif content:
            self.title = f"{content[:93]}..." if len(content) > 96 else content
        elif embeds and isinstance(embeds, Embed) and embeds.title:
            self.title = f"{embeds.title[:93]}..." if len(embeds.title) > 96 else embeds.title
        elif embeds and isinstance(embeds, list) and embeds[0].title:
            self.title = next(
                (
                    f"{embed.title[:93]}..." if len(embed.title) > 96 else embed.title
                    for embed in embeds
                    if embed.title
                ),
                "No title",
            )
        else:
            self.title = "No title"

        super().__init__(
            content=content,
            embeds=embeds,
        )

    def __repr__(self) -> str:
        return f"<Page content={self.content}, embeds={self.embeds}>"

    __str__ = __repr__


class Paginator(DictSerializerMixin):
    """
    The paginator.

    Parameters:

    - `client: Client`: The client.
    - `ctx: CommandContext | ComponentContext`: The context.
    - `pages: list[Page]`: The pages to paginate.
    - `?timeout: int | float | None`: The timeout in seconds. Defaults to 60.
    - `?author_only: bool`: Whether to only allow the author to edit the message. Defaults to False.
    - `?use_buttons: bool`: Whether to use buttons. Defaults to True.
    - `?use_select: bool`: Whether to use the select menu. Defaults to True.
    - `?use_index: bool`: Whether the paginator should use the index button. Defaults to False.
    - `?extended_buttons: bool`: Whether to use extended buttons. Defaults to True.
    - `?buttons: dict[str, Button]`: The customized buttons to use. Defaults to None. Use `ButtonKind` as the key.
    - `?placeholder: str`: The placeholder to use for the select menu. Defaults to "Page".
    - `?disable_after_timeout: bool`: Whether to disable the components after timeout. Defaults to True.
    - `?remove_after_timeout: bool`: Whether to remove the components after timeout. Defaults to False.
    - `?func_before_edit: Callable`: The function to run before editing the message.
    - `?func_after_edit: Callable`: The function to run after editing the message.

    Methods:

    - *async* `run() -> ?Data`: Runs the paginator in a loop until timed out.
    - *property* `custom_ids -> list[str]`: The custom IDs of the components.
    - *async* `component_logic()`: The logic for the components when clicked.
    - *async* `check(ctx: ComponentContext) -> bool`: Whether the paginator is for the user.
    - *func* `select_row() -> ?ActionRow`: The select action row.
    - *func* `buttons_row() -> ?ActionRow`: The buttons action row.
    - *func* `components() -> list[?ActionRow]`: The components as action rows.
    - *async* `send() -> Message`: Sends the paginator.
    - *async* `edit() -> Message`: Edits the paginator.
    - *func* `disabled_components() -> list[?ActionRow]`: The disabled components as action rows.
    - *func* `removed_components()`: The removed components.
    - *async* `end_paginator()`: Ends the paginator.
    - *async* `run_function(func: Callable) -> bool`: Runs a function.
    - *func* `data() -> Data`: The data of the paginator.
    """

    __slots__ = (
        "_json",
        "client",
        "ctx",
        "pages",
        "timeout",
        "author_only",
        "use_buttons",
        "use_select",
        "use_index",
        "extended_buttons",
        "buttons",
        "placeholder",
        "disable_after_timeout",
        "remove_after_timeout",
        "func_before_edit",
        "func_after_edit",
        "id",
        "component_ctx",
        "index",
        "top",
        "is_dict",
        "is_embeds",
        "message",
        "_msg",
    )
    _json: Dict[str, Any]
    client: Client
    ctx: Union[CommandContext, ComponentContext]
    pages: List[Page]
    timeout: Optional[Union[int, float]]
    author_only: bool
    use_buttons: bool
    use_select: bool
    use_index: bool
    extended_buttons: bool
    buttons: Optional[Dict[str, Button]]
    placeholder: str
    disable_after_timeout: bool
    remove_after_timeout: bool
    func_before_edit: Optional[Union[Callable, Coroutine]]
    func_after_edit: Optional[Union[Callable, Coroutine]]
    id: int
    component_ctx: Optional[ComponentContext]
    index: int
    top: int
    is_dict: bool
    is_embeds: bool
    message: Message
    _msg: Dict[str, Optional[Snowflake]]

    def __init__(
        self,
        client: Client,
        ctx: Union[CommandContext, ComponentContext],
        pages: List[Page],
        timeout: Optional[Union[int, float]] = 60,
        author_only: bool = False,
        use_buttons: bool = True,
        use_select: bool = True,
        use_index: bool = False,
        extended_buttons: bool = True,
        buttons: Optional[Dict[str, Button]] = None,
        placeholder: str = "Page",
        disable_after_timeout: bool = True,
        remove_after_timeout: bool = False,
        func_before_edit: Optional[Union[Callable, Coroutine]] = None,
        func_after_edit: Optional[Union[Callable, Coroutine]] = None,
        **kwargs,
    ) -> None:
        if not (use_buttons or use_select):
            raise PaginatorWontWork(
                "You need either buttons, select, or both, or else the paginator wont work!"
            )
        if len(pages) < 2:
            raise PaginatorWontWork("You need more than one page!")
        if not all(isinstance(page, Page) for page in pages):
            raise PaginatorWontWork("All pages must be of type `Page`!")
        if not hasattr(client, "wait_for_component"):
            setup(client)

        super().__init__(
            client=client,
            ctx=ctx,
            pages=pages,
            timeout=timeout,
            author_only=author_only,
            use_buttons=use_buttons,
            use_select=use_select,
            use_index=use_index,
            extended_buttons=extended_buttons,
            buttons={} if buttons is None else buttons,
            placeholder=placeholder,
            disable_after_timeout=disable_after_timeout,
            remove_after_timeout=remove_after_timeout,
            func_before_edit=func_before_edit,
            func_after_edit=func_after_edit,
            **kwargs,
        )
        self.id: int = kwargs.get("id", randint(0, 999_999_999))
        self.component_ctx: Optional[ComponentContext] = kwargs.get("component_ctx")
        self.index: int = kwargs.get("index", 0)
        self.top: int = kwargs.get("top", len(pages) - 1)
        self.message: Optional[Message] = kwargs.get("message")
        self._msg = {"message_id": None, "channel_id": self.ctx.channel_id}

    async def run(self) -> Data:
        self.message = await self.send()
        self._msg["message_id"] = self.message.id
        if not self.message._client:
            self.message._client = self.client._http
            self.message.channel_id = self.ctx.channel_id
        while True:
            try:
                self.component_ctx: ComponentContext = await wait_for_component(
                    self.client,
                    self.custom_ids,
                    self.message.id,
                    self.check,
                    self.timeout,
                )
            except TimeoutError:
                await self.end_paginator()
                return self.data()
            result: Optional[bool] = None
            if self.func_before_edit is not None:
                try:
                    result: Optional[bool] = await self.run_function()
                except StopPaginator:
                    return self.data()
                if result is False:
                    continue
            await self.component_logic()
            self.message = await self.edit()
            if not self.message._client:
                self.message._client = self.client._http
                self.message.channel_id = self.ctx.channel_id
                self.message.id = self._msg["message_id"]
            if self.func_after_edit is not None:
                try:
                    result: Optional[bool] = await self.run_function()
                except StopPaginator:
                    return self.data()
                if result is False:
                    continue

    @property
    def custom_ids(self) -> List[str]:
        return [
            f"select{self.id}",
            f"first{self.id}",
            f"prev{self.id}",
            f"index{self.id}",
            f"next{self.id}",
            f"last{self.id}",
        ]

    async def component_logic(self) -> None:
        custom_id: str = self.component_ctx.data.custom_id
        if custom_id == f"select{self.id}":
            self.index = int(self.component_ctx.data.values[0]) - 1
        elif custom_id == f"first{self.id}":
            self.index = 0
        elif custom_id == f"prev{self.id}":
            self.index -= 1
            self.index = max(self.index, 0)
        elif custom_id == f"next{self.id}":
            self.index += 1
            self.index = min(self.index, self.top)
        elif custom_id == f"last{self.id}":
            self.index = self.top

    async def check(self, ctx: ComponentContext) -> bool:
        boolean: bool = True
        if self.author_only:
            boolean = ctx.user.id == self.ctx.user.id
        if not boolean:
            await ctx.send("This paginator is not for you!", ephemeral=True)
        return boolean

    def select_row(self) -> Optional[ActionRow]:
        if not self.use_select or len(self.pages) > 25:
            return

        select_options = [
            SelectOption(label=f"{page_num}: {page.title}", value=page_num)
            for page_num, page in enumerate(self.pages, start=1)
        ]

        select = SelectMenu(
            options=select_options,
            custom_id=f"select{self.id}",
            placeholder=f"{self.placeholder} {self.index + 1}/{self.top + 1}",
            min_values=1,
            max_values=1,
        )
        return ActionRow(components=[select])

    def buttons_row(self) -> Optional[ActionRow]:
        if not self.use_buttons:
            return

        disabled_left = self.index == 0
        disabled_right = self.index == self.top
        buttons = [
            self.buttons.get("first", Button(style=1, emoji=Emoji(name="⏮️")))
            if self.extended_buttons
            else None,
            self.buttons.get("prev", Button(style=1, emoji=Emoji(name="◀️"))),
            self.buttons.get(
                "index",
                Button(style=1, label=f"{self.placeholder} {self.index + 1}/{self.top + 1}"),
            )
            if self.use_index
            else None,
            self.buttons.get("next", Button(style=1, emoji=Emoji(name="▶️"))),
            self.buttons.get("last", Button(style=1, emoji=Emoji(name="⏭️")))
            if self.extended_buttons
            else None,
        ]

        for i, button in enumerate(buttons):
            if button is None:
                continue
            button.custom_id = self.custom_ids[i + 1]
            button._json.update({"custom_id": button.custom_id})
            button.disabled = (
                disabled_left
                if button.custom_id in self.custom_ids[1:3]
                else True
                if button.custom_id == self.custom_ids[3]
                else disabled_right
            )
            button._json.update({"disabled": button.disabled})
            if button.custom_id == self.custom_ids[3]:
                button.label = f"{self.placeholder} {self.index + 1}/{self.top + 1}"
                button._json.update({"label": button.label})

        return ActionRow(components=list(filter(None, buttons)))

    def components(self) -> List[ActionRow]:
        return list(filter(None, [self.select_row(), self.buttons_row()]))

    async def send(self) -> Message:
        return await self.ctx.send(components=self.components(), **self.pages[self.index]._json)

    async def edit(self) -> Message:
        return await self.component_ctx.edit(
            components=self.components(), **self.pages[self.index]._json
        )

    def disabled_components(self) -> List[ActionRow]:
        components = self.components()
        for action_row in components:
            for component in action_row.components:
                component.disabled = True
        return components

    def removed_components(self) -> None:
        return

    async def end_paginator(self) -> None:
        await self.message.edit(
            components=self.removed_components()
            if self.remove_after_timeout
            else self.disabled_components()
            if self.disable_after_timeout
            else MISSING
        )

    async def run_function(self, func) -> bool:
        if func is not None:
            if iscoroutinefunction(func):
                return await func(self, self.component_ctx)
            else:
                return func(self, self.component_ctx)

    def data(self) -> Data:
        return Data(
            paginator=self,
            original_ctx=self.ctx,
            component_ctx=self.component_ctx,
            message=self.message,
        )

    def __repr__(self) -> str:
        return f"<Paginator id={self.id}>"

    __str__ = __repr__

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "_json":
            object.__setattr__(self, "_json", __value)
        elif __name in self.__slots__:
            self._json.update({__name: __value})
        return super().__setattr__(__name, __value)
