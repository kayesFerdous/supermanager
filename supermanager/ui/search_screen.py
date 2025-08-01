from __future__ import annotations
from typing import TYPE_CHECKING

from textual.screen import ModalScreen
from textual.widgets import Input
from textual import events
from textual.app import ComposeResult
import asyncio

if TYPE_CHECKING:
    from .dir_viewer_app import DirViewerApp


class SearchScreen(ModalScreen):
    def __init__(self, app_ref: "DirViewerApp", **kwargs) -> None:
        super().__init__(**kwargs)
        self.app_ref = app_ref
        self.search_task = None

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for an item...")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    async def on_input_changed(self, event: Input.Changed) -> None:
        if self.search_task:
            self.search_task.cancel()
        self.search_task = asyncio.create_task(
            self.app_ref.update_search(event.value)
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.search_task:
            self.search_task.cancel()
        self.dismiss()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            if self.search_task:
                self.search_task.cancel()
            # Clear the search results by loading the full directory
            await self.app_ref.update_search("")
            self.dismiss()