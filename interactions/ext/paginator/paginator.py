from asyncio import TimeoutError
from enum import Enum
from inspect import iscoroutinefunction
from random import randint
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions.ext.wait_for import setup, wait_for_component

from interactions import (
    ActionRow,
    Button,
    Client,
    CommandContext,
    ComponentContext,
    DictSerializerMixin,
    Embed,
    Emoji,
    Message,
    SelectMenu,
    SelectOption,
)

from .errors import PaginatorWontWork, StopPaginator


class ButtonKind(str, Enum):
    """Enum for button types."""

    FIRST = "first"
    PREVIOUS = "prev"
    NEXT = "next"
    LAST = "last"


class Data(DictSerializerMixin):
    __slots__ = ("_json", "paginator", "original_ctx", "component_ctx", "message")
    _json: Dict[str, Any]
    paginator: "Paginator"
    original_ctx: Union[CommandContext, ComponentContext]
    component_ctx: ComponentContext
    message: Message

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


class Paginator(DictSerializerMixin):
    __slots__ = (
        "_json",
        "client",
        "ctx",
        "pages",
        "timeout",
        "author_only",
        "use_buttons",
        "use_select",
        "extended_buttons",
        "buttons",
        "select_placeholder",
        "func_before_edit",
        "func_after_edit",
        "id",
        "component_ctx",
        "index",
        "top",
        "is_dict",
        "is_embeds",
        "message",
    )
    _json: Dict[str, Any]
    client: Client
    ctx: Union[CommandContext, ComponentContext]
    pages: Union[List[str], List[Embed], Dict[str, Embed]]
    timeout: Optional[Union[int, float]]
    author_only: Optional[bool]
    use_buttons: Optional[bool]
    use_select: Optional[bool]
    extended_buttons: Optional[bool]
    buttons: Optional[Dict[str, Button]]
    select_placeholder: Optional[str]
    func_before_edit: Optional[Union[Callable, Coroutine]]
    func_after_edit: Optional[Union[Callable, Coroutine]]
    id: int
    component_ctx: Optional[ComponentContext]
    index: int
    top: int
    is_dict: bool
    is_embeds: bool
    message: Message

    def __init__(
        self,
        client: Client,
        ctx: Union[CommandContext, ComponentContext],
        pages: Union[List[Embed], List[str], Dict[str, Embed]],
        timeout: Optional[Union[int, float]] = None,
        author_only: Optional[bool] = False,
        use_buttons: Optional[bool] = True,
        use_select: Optional[bool] = True,
        extended_buttons: Optional[bool] = True,
        buttons: Optional[Dict[str, Button]] = None,
        select_placeholder: Optional[str] = "Page",
        func_before_edit: Optional[Union[Callable, Coroutine]] = None,
        func_after_edit: Optional[Union[Callable, Coroutine]] = None,
        **kwargs,
    ) -> None:
        if not hasattr(client, "wait_for_component"):
            setup(client)
        if not (use_buttons or use_select):
            raise PaginatorWontWork(
                "You need either buttons, select, or both, or else the paginator wont work!"
            )

        super().__init__(
            client=client,
            ctx=ctx,
            pages=pages,
            timeout=timeout,
            author_only=author_only,
            use_buttons=use_buttons,
            use_select=use_select,
            extended_buttons=extended_buttons,
            buttons={} if buttons is None else buttons,
            select_placeholder=select_placeholder,
            func_before_edit=func_before_edit,
            func_after_edit=func_after_edit,
            **kwargs,
        )
        self.id: int = kwargs.get("id", randint(0, 999_999_999))
        self.component_ctx: Optional[ComponentContext] = kwargs.get("component_ctx")
        self.index: int = kwargs.get("index", 0)
        self.top: int = kwargs.get("top", len(pages) - 1)
        self.message: Message = kwargs.get("message")
        self.is_dict: bool = isinstance(pages, dict)
        self.is_embeds: bool = isinstance(pages, list) and all(
            isinstance(page, Embed) for page in pages
        )

        self._json.update(
            {
                "id": self.id,
                "component_ctx": self.component_ctx,
                "index": self.index,
                "top": self.top,
                "message": self.message,
            }
        )

    async def run(self) -> Data:
        self.message = await self.send()
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
        if not self.use_select:
            return
        select_options = []
        if self.is_dict:
            for content, embed in self.pages.items():
                page_num: str = str(list(self.pages).index(content) + 1)
                title: Optional[str] = embed.title
                label: str = (
                    f'{page_num}: {f"{title[:93]}..." if len(title) > 96 else title}'
                    if title
                    else f'{page_num}: {f"{content[:93]}..." if len(content) > 96 else content}'
                )

                select_options.append(SelectOption(label=label, value=page_num))
        else:
            for content in self.pages:
                page_num: str = str(self.pages.index(content) + 1)
                if not self.is_embeds:
                    label: str = f'{page_num}: {f"{content[:93]}..." if len(content) > 96 else content}'
                else:
                    embed: Embed = content
                    if embed.title is not None:
                        label: str = f'{page_num}: {f"{embed.title[:93]}..." if len(embed.title) > 96 else embed.title}'
                    else:
                        label: str = f"{page_num}: No title"
                select_options.append(SelectOption(label=label, value=page_num))

        select = SelectMenu(
            options=select_options,
            custom_id=f"select{self.id}",
            placeholder=f"{self.select_placeholder} {self.index + 1}/{self.top + 1}",
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
                else disabled_right
            )
            button._json.update(
                {
                    "disabled": disabled_left
                    if button.custom_id in self.custom_ids[1:3]
                    else disabled_right
                }
            )
        return ActionRow(components=list(filter(None, buttons)))

    def components(self) -> List[ActionRow]:
        return list(filter(None, [self.select_row(), self.buttons_row()]))

    async def send(self) -> Message:
        if self.is_dict:
            return await self.ctx.send(
                list(self.pages.keys())[self.index],
                embeds=list(self.pages.values())[self.index],
                components=self.components(),
            )
        else:
            return await self.ctx.send(
                self.pages[self.index],
                components=self.components(),
            )

    async def edit(self, components: Optional[List[ActionRow]] = None) -> Message:
        if self.is_dict:
            return await self.component_ctx.edit(
                list(self.pages.keys())[self.index],
                embeds=list(self.pages.values())[self.index],
                components=components if components is not None else self.components(),
            )
        else:
            return await self.component_ctx.edit(
                self.pages[self.index],
                components=components if components is not None else self.components(),
            )

    async def end_paginator(self) -> None:
        components = self.components()
        for action_row in components:
            for component in action_row.components:
                component.disabled = True
        ...  # TODO: implement message editing

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
