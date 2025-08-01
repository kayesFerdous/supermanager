from textual import events
from textual.screen import ModalScreen
from textual.widgets import Input
from textual.app import ComposeResult

class AddItemScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter name (add / for directory)")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)


    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss()
