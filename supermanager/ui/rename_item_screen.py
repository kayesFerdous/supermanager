from textual import events
from textual.screen import ModalScreen
from textual.widgets import Input
from textual.app import ComposeResult

class RenameItemScreen(ModalScreen):
    def __init__(self, original_name: str, **kwargs):
        super().__init__(**kwargs)
        self.original_name = original_name

    def compose(self) -> ComposeResult:
        yield Input(value=self.original_name, placeholder="Enter new name")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value and value != self.original_name:
            self.dismiss(value)
        else:
            self.dismiss(None)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(None)
