from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Markdown
from textual.events import Key

KEYMAP_TABLE = """
| Category      | Key(s)              | Action                |
|---------------|---------------------|-----------------------|
| **Navigation**  | `up`, `k`           | Move Cursor Up        |
|               | `down`, `j`         | Move Cursor Down      |
|               | `right`, `l`, `enter` | Go Into Directory     |
|               | `left`,`h` , `backspace`         | Go to Parent Directory|
|               | `q`                 | Quit the App          |
| **File Operations**    | `d`                 | Delete Selected       |
|               | `a`                 | Create New Item       |
|               | `c`                 | Copy Selected         |
|               | `p`                 | Paste from Clipboard  |
|               | `m`                 | Move Selected         |
|               | `b`                 | Bookmark/Pin Item     |
|               | `f7`                | Change Permissions    |
| **Selection**   | `space`             | Toggle Selection      |
|               | `escape`            | Clear All Selections  |
| **UI & View**   | `H`                 | Toggle Hidden Files   |
|               | `s`                 | Search Current View   |
|               | `tab`               | Cycle Focus           |
|               | `f1`                | Show This Help Screen |
|               | `ctrl+t`            | Toggle Footer         |
"""

class KeymapHelpScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Keymap Help", id="keymap-title")
        yield Markdown(KEYMAP_TABLE, id="keymap-content")

    def on_key(self, event: Key) -> None:
        self.app.pop_screen()
