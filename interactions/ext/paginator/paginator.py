from asyncio import TimeoutError
from enum import Enum
from random import randint
from typing import Dict, List, Optional, Union

from interactions.ext.wait_for import setup, wait_for_component

from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    Client,
    CommandContext,
    ComponentContext,
    DictSerializerMixin,
    Embed,
    Emoji,
    Message,
)


class ButtonKind(str, Enum):
    """
    Enum for button types.
    """

    FIRST = "first"
    PREVIOUS = "prev"
    NEXT = "next"
    LAST = "last"


class ButtonConfig:
    def __init__(
        self,
        style: ButtonStyle,
        label: str,
        emoji: Optional[Emoji] = None,
        disabled: Optional[bool] = False,
    ):
        self.kind = None
        self.kwargs = {
            "style": style,
            "label": label,
            "emoji": emoji,
            "disabled": disabled,
        }


class Data(DictSerializerMixin):
    __slots__ = ("paginator", "original_ctx", "component_ctx", "message")
    paginator: "Paginator"
    original_ctx: Union[CommandContext, ComponentContext]
    component_ctx: ComponentContext
    message: Message

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Paginator(DictSerializerMixin):
    __slots__ = (
        "_json",
        "client",
        "ctx",
        "pages",
        "timeout",
        "author_only",
        "buttons",
        "id",
        "component_ctx",
        "index",
        "top",
        "is_dict",
        "message",
    )
    client: Client
    ctx: Union[CommandContext, ComponentContext]
    pages: Union[List[str], Dict[str, Embed]]
    timeout: Optional[Union[int, float]]
    author_only: Optional[bool]
    buttons: Optional[List[Button]]
    id: int
    component_ctx: Optional[ComponentContext]
    index: int
    top: int
    is_dict: bool
    message: Message

    def __init__(
        self,
        client: Client,
        ctx: Union[CommandContext, ComponentContext],
        pages: Union[List[Embed], List[str], Dict[str, Embed]],
        timeout: Optional[Union[int, float]] = None,
        author_only: Optional[bool] = False,
        buttons: Optional[List[Button]] = None,
        **kwargs,
    ) -> None:
        if not hasattr(client, "wait_for_component"):
            setup(client)

        super().__init__(
            client=client,
            ctx=ctx,
            pages=pages,
            timeout=timeout,
            author_only=author_only,
            buttons={} if buttons is None else buttons,
            **kwargs,
        )
        self.id: int = kwargs.get("id", randint(0, 999_999))
        self.component_ctx: Optional[ComponentContext] = None
        self.index: int = kwargs.get("index", 0)
        self.top: int = kwargs.get("top", len(pages) - 1)
        self.is_dict: bool = isinstance(pages, dict)
        self.message: Message = None

        self._json.update(
            {
                "id": self.id,
                "index": self.index,
                "top": self.top,
                "message": self.message,
            }
        )

    async def run(self):
        self.message = await self.send()
        while True:
            try:
                self.component_ctx: ComponentContext = await wait_for_component(
                    self.client,
                    self.custom_ids,
                    check=self.check,
                    timeout=self.timeout,
                )
            except TimeoutError:
                await self.disable_components()
                return Data(
                    paginator=self,
                    original_ctx=self.ctx,
                    component_ctx=self.component_ctx,
                    message=self.message,
                )
            await self.component_logic()
            self.message = await self.edit()

    @property
    def custom_ids(self):
        return [
            f"first{self.id}",
            f"prev{self.id}",
            f"next{self.id}",
            f"last{self.id}",
        ]

    async def component_logic(self):
        custom_id: str = self.component_ctx.data.custom_id
        if custom_id == f"first{self.id}":
            self.index = 0
        elif custom_id == f"prev{self.id}":
            self.index -= 1
            self.index = max(self.index, 0)
        elif custom_id == f"next{self.id}":
            self.index += 1
            self.index = min(self.index, self.top)
        elif custom_id == f"last{self.id}":
            self.index = self.top

    async def check(self, ctx) -> bool:
        if self.author_only:
            return self.component_ctx.user.id == self.ctx.user.id
        return True

    def buttons_row(self) -> ActionRow:
        disabled_left = self.index == 0
        disabled_right = self.index == self.top
        kwargs = {key: value.kwargs for key, value in self.buttons.items()}
        return ActionRow(
            components=[
                kwargs.get(
                    "first",
                    Button(
                        style=1,
                        emoji=Emoji(name="⏪"),
                        custom_id=f"first{self.id}",
                        disabled=disabled_left,
                    ),
                ),
                kwargs.get(
                    "prev",
                    Button(
                        style=1,
                        emoji=Emoji(name="◀"),
                        custom_id=f"prev{self.id}",
                        disabled=disabled_left,
                    ),
                ),
                kwargs.get(
                    "next",
                    Button(
                        style=1,
                        emoji=Emoji(name="▶"),
                        custom_id=f"next{self.id}",
                        disabled=disabled_right,
                    ),
                ),
                kwargs.get(
                    "last",
                    Button(
                        style=1,
                        emoji=Emoji(name="⏩"),
                        custom_id=f"last{self.id}",
                        disabled=disabled_right,
                    ),
                ),
            ]
        )

    def components(self) -> List[ActionRow]:
        return list(filter(None, [self.buttons_row()]))

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

    async def edit(self, components=None) -> Message:
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

    async def disable_components(self):
        components = self.components()
        for action_row in components:
            for component in action_row.components:
                component.disabled = True
        # if not hasattr(self.message, "_client") or not self.message._client:
        #     self.message = Message(**self.message._json, _client=self.client._http)
        # await self.message.edit(components=components)
