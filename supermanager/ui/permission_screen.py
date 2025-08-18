from textual.screen import ModalScreen
from textual.widgets import Input, ListView, ListItem, Label, Static
from textual.app import ComposeResult
from textual.containers import Vertical
from textual import events

PRESETS = [
    ("755", "rwxr-xr-x"),
    ("644", "rw-r--r--"),
    ("700", "rwx------"),
    ("600", "rw-------"),
    ("+x",  "Add user execute"),
    ("a+x", "Add execute for all"),
]

class PermissionScreen(ModalScreen):
    """Modal to choose a permission preset or enter a custom octal mode.

    Keyboard:
      j / k or down / up : move in presets
      tab                : toggle between presets and input
      enter (in list)    : select highlighted preset
      enter (in input)   : submit custom mode
      esc                : cancel
    """

    def compose(self) -> ComposeResult:
        # Build list items up front to avoid calling append before the ListView is mounted
        items = [ListItem(Label(f" {mode:<4} {desc}"), name=mode) for mode, desc in PRESETS]
        with Vertical():
            yield Static("Select permission (Tab to input, Enter to apply)", id="perm-header")
            yield ListView(*items, id="perm-presets")
            yield Input(placeholder="Custom mode e.g. 755 / 0644 / +x", id="perm-input")

    def on_mount(self) -> None:
        lv = self.query_one(ListView)
        lv.focus()
        # Ensure first item visually active
        if lv.children:
            lv.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.dismiss(event.item.name)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value:
            self.dismiss(value)
        else:
            self.dismiss(None)

    def on_key(self, event: events.Key) -> None:
        lv = self.query_one(ListView)
        inp = self.query_one(Input)
        key = event.key

        if key == "escape":
            self.dismiss(None)
            return

        if key == "tab":
            if lv.has_focus:
                inp.focus()
            else:
                lv.focus()
            event.stop()
            return

        if lv.has_focus:
            if key in ("j", "down"):
                lv.action_cursor_down()
                event.stop()
                return
            if key in ("k", "up"):
                lv.action_cursor_up()
                event.stop()
                return
            if key == "enter":
                highlighted = getattr(lv, "highlighted_child", None)
                if highlighted is not None:
                    self.dismiss(highlighted.name)
                event.stop()
                return
        # Input handles Enter itself; no extra handling here
