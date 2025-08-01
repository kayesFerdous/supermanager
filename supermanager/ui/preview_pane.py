import os
from textual.app import ComposeResult
from textual.widgets import Static



class PreviewPane(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = Static("Select a file to preview")

    def compose(self) -> ComposeResult:
        yield self.content

    def update_preview(self, path: str = ""):
        self.border_title = "| Preview |"
        if not path:
            self.content.update("No item selected")
            return

        if os.path.isdir(path):
            try:
                entries = os.listdir(path)
                dir_listing = "\n".join(entries)
                self.content.update(f"Directory contents:\n\n{dir_listing}")
            except Exception as e:
                self.content.update(f"Error reading folder: {e}")
        elif os.path.isfile(path):
            try:
                _, extension = os.path.splitext(path)
                if extension.lower() in [".png", ".jpg", ".jpeg", ".gif"]:
                    self.content.update(f"Image file: {os.path.basename(path)}")
                elif extension.lower() in [".pdf", ".zip", ".tar", ".gz"]:
                    self.content.update(f"Unsupported file type: {os.path.basename(path)}")
                else:
                    with open(path, "r", encoding="utf-8") as f:
                        self.content.update(f.read(1024)) # Preview first 1024 bytes
            except Exception as e:
                self.content.update(f"Error reading file: {e}")
        else:
            self.content.update("Unsupported file type")

