from textual.screen import ModalScreen
from textual.widgets import Label
from textual import events
from textual.app import ComposeResult

class ConfirmationScreen(ModalScreen):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Label(f"{self.message} (y/n)")

    def on_key(self, event: events.Key) -> None:
        if event.key == "y":
            self.dismiss(True)
        elif event.key == "n":
            self.dismiss(False)
        elif event.key == "escape":
            self.dismiss()
