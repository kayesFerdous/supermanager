import subprocess
import shutil
from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label, Static
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
import os
import asyncio
import stat
from datetime import datetime

from .preview_pane import PreviewPane
from supermanager.ui.fileicons import FILE_ICONS
from .. import actions
from .confirmation_screen import ConfirmationScreen
from .add_item_screen import AddItemScreen
from .rename_item_screen import RenameItemScreen
from .permission_screen import PermissionScreen
from .keymap_help_screen import KeymapHelpScreen
from .search_screen import SearchScreen
from .fileicons import FILE_ICONS


class DirViewerApp(App):
    CSS_PATH = os.path.join(os.path.dirname(__file__), "../dir.tcss")

    FILE_ICONS = FILE_ICONS
    def __init__(self, initial_dir: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.show_hidden = False
        self.selected_items = set()
        self.initial_dir = initial_dir
        self.home_sidebar_first_focus = True
        self.sidebar_first_focus = True

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                with Vertical(id="sidebar-container"):
                    self.home_sidebar = ListView(id="home-sidebar")
                    yield self.home_sidebar

                    self.sidebar = ListView(id="sidebar")
                    yield self.sidebar
                with Vertical(id="file-list-container"):
                    yield Static(id="file-list-header")
                    self.list_view = ListView(id="file-list")
                    yield self.list_view
                self.preview_pane = PreviewPane(id="preview-pane")
                yield self.preview_pane
            with Horizontal(id="footer"):
                yield Static(id="footer-left")
                yield Static(id="footer-middle")
                yield Static(id="footer-right")

    def update_highlight_indicators(self, list_view):
        """Update the highlight indicators for a specific ListView"""
        for i, item in enumerate(list_view.children):
            if hasattr(item, 'children') and len(item.children) > 0:
                horizontal = item.children[0]
                if hasattr(horizontal, 'children') and len(horizontal.children) > 0:
                    indicator_label = horizontal.children[0]
                    if i == list_view.index:
                        indicator_label.update("")
                        indicator_label.add_class("highlight-indicator")
                    else:
                        indicator_label.update(" ")
                        indicator_label.remove_class("highlight-indicator")

    async def on_mount(self):
        header = self.query_one("#file-list-header", Static)
        header.border_title = " Directory "

        home_sidebar = self.query_one("#home-sidebar", ListView)
        home_sidebar.border_title = " supermanager "

        sidebar = self.query_one("#sidebar", ListView)
        sidebar.border_title = "   Pinned "

        if self.initial_dir:
            self.current_dir = os.path.abspath(self.initial_dir)
        else:
            self.current_dir = os.path.abspath(".")
        # Navigation
        self.bind("q", "quit", description="Quit", show=False)
        self.bind("up,k", "cursor_up", description="Up")
        self.bind("down,j", "cursor_down", description="Down")
        self.bind("left,h", "go_up", description="Go Up")
        self.bind("right,l", "go_in", description="Go In")
        self.bind("enter", "go_in", show=False, description="Go In")
        self.bind("backspace", "go_up", show=False, description="Go Up")

        # File Operations
        self.bind("d", "delete_item", description="Delete")
        self.bind("a", "add_item", description="New Item")
        self.bind("c", "copy_selected_items", description="Copy")
        self.bind("p", "paste_items", description="Paste")
        self.bind("m", "move_items", description="Move")
        self.bind("b", "pin_item", description="Bookmark")
        self.bind("r", "rename_item", description="Rename")
        self.bind("f7", "change_permissions", description="Chmod")

        # Selection
        self.bind("space", "toggle_selection", description="Select")
        self.bind("escape", "clear_selection", description="Clear Selection")

        # UI
        self.bind("H", "toggle_hidden", description="Toggle Hidden")
        self.bind("s", "search", description="Search")
        self.bind("tab", "toggle_focus", description="Cycle Focus")
        self.bind("f1", "show_keymap_help", description="Help")
        self.bind("ctrl+t", "toggle_footer", description="Toggle Footer")
        
        await self.update_home_sidebar()
        await self.update_sidebar()
        await self.load_directory()
        self.list_view.focus()
        await self.update_status_bar()
        

    async def load_directory(self, entries=None):
        self.list_view.clear()
        abs_path = os.path.abspath(self.current_dir)

        header = self.query_one("#file-list-header", Static)
        header.update(f"󰉋 {abs_path}")

        if entries is None:
            entries = actions.get_directory_entries(abs_path, self.show_hidden)

        for entry in entries:
            if not entry:
                continue
            
            parts = entry.split("|", 1)
            if len(parts) != 2:
                continue

            entry_type, name = parts
            icon = "󰉋"  # Default icon for directories
            if entry_type == "file":
                file_extension = os.path.splitext(name)[1].lower()
                icon = self.FILE_ICONS.get(file_extension, "󰈙")  # Default icon for files
            list_item = ListItem(
                Horizontal(
                    Label(" ", classes="highlight-indicator"),
                    Label(f" {icon} {os.path.basename(name)}")
                ),
                name=f"{entry_type}|{name}"
            )
            await self.list_view.append(list_item)

        if self.list_view.children:
            self.list_view.index = 0  # Default to first item
            for i, item in enumerate(self.list_view.children):

                entry_type, _ = item.name.split("|", 1)
                if entry_type == "dir":
                    self.list_view.index = i
                    break
        
        # Update indicators after loading
        self.update_highlight_indicators(self.list_view)
        await self.on_list_view_highlighted()

    
    async def on_list_view_selected(self, event: ListView.Selected):
        if event.list_view.id == "file-list":
            await self.action_go_in()
        elif event.list_view.id == "sidebar":
            selected = event.item
            
            entry_type, path = selected.name.split("|", 1)

            if entry_type == "dir":
                self.current_dir = path
                self.selected_items.clear()
                await self.load_directory()
                await self.update_status_bar()
                self.list_view.focus()
        elif event.list_view.id == "home-sidebar":
            selected = event.item
            entry_type, path = selected.name.split("|", 1)

            if entry_type == "dir":
                self.current_dir = path
                self.selected_items.clear()
                await self.load_directory()
                await self.update_status_bar()
                self.list_view.focus()

    async def on_list_view_highlighted(self, event: ListView.Highlighted = None):
        # Update indicators for all list views when highlight changes
        self.update_highlight_indicators(self.list_view)
        self.update_highlight_indicators(self.home_sidebar)
        self.update_highlight_indicators(self.sidebar)
        
        if self.list_view.highlighted_child:
            entry_type, name = self.list_view.highlighted_child.name.split("|", 1)
            full_path = os.path.join(self.current_dir, os.path.basename(name))
            self.preview_pane.update_preview(full_path)
            await self.update_footer_middle(full_path)
        else:
            self.preview_pane.update_preview("")
            await self.update_footer_middle(None)


    async def update_search(self, query: str):
        # A small delay to prevent spamming searches on every keystroke
        await asyncio.sleep(0.05) 
        if query:
            entries = await actions.find_item(self.current_dir, query)
            await self.load_directory(entries)
        else:
            # If query is empty, load the original directory view
            await self.load_directory()

    async def action_search(self):
        self.push_screen(SearchScreen(app_ref=self))

    async def action_cursor_down(self):
        if self.sidebar.has_focus:
            self.sidebar.action_cursor_down()
            self.update_highlight_indicators(self.sidebar)
        elif self.home_sidebar.has_focus:
            self.home_sidebar.action_cursor_down()
            self.update_highlight_indicators(self.home_sidebar)
        else:
            self.list_view.action_cursor_down()
            self.update_highlight_indicators(self.list_view)
        await self.on_list_view_highlighted()

    async def action_cursor_up(self):
        if self.sidebar.has_focus:
            self.sidebar.action_cursor_up()
            self.update_highlight_indicators(self.sidebar)
        elif self.home_sidebar.has_focus:
            self.home_sidebar.action_cursor_up()
            self.update_highlight_indicators(self.home_sidebar)
        else:
            self.list_view.action_cursor_up()
            self.update_highlight_indicators(self.list_view)
        await self.on_list_view_highlighted()

    def _toggle_current_item_selection(self):
        try:
            current_item = self.list_view.highlighted_child
            if current_item:
                if current_item in self.selected_items:
                    self.selected_items.remove(current_item)
                    current_item.remove_class("selected")
                else:
                    self.selected_items.add(current_item)
                    current_item.add_class("selected")
        except NoMatches:
            pass # No item highlighted

    async def action_toggle_selection(self):
        self._toggle_current_item_selection()
        actions.log_debug(f"Selected items: {len(self.selected_items)}")
        await self.update_status_bar()

    async def action_clear_selection(self):
        for item in self.selected_items:
            item.remove_class("selected")
        self.selected_items.clear()
        await self.update_status_bar()
        await self.update_footer_middle(None)

    async def action_go_in(self):
        index = self.list_view.index
        if index is not None:
            selected = self.list_view.children[index]
            entry_type, name = selected.name.split("|", 1)

            if entry_type == "dir":
                self.current_dir = os.path.join(self.current_dir, os.path.basename(name))
                self.selected_items.clear() 
                await self.load_directory()
                await self.update_status_bar()
            else:
                full_path = os.path.join(self.current_dir, os.path.basename(name))
                try:
                    subprocess.run(["xdg-open", full_path], check=True)
                except FileNotFoundError:
                    print(f"Error: xdg-open not found. Cannot open {os.path.basename(name)}")
                except Exception as e:
                    print(f"Error opening {os.path.basename(name)}: {e}")

    async def action_go_up(self):
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:
            self.current_dir = parent_dir
            self.selected_items.clear() 
            await self.load_directory()
            await self.update_status_bar()

    async def action_delete_item(self):
        if self.selected_items:
            message = f"Delete {len(self.selected_items)} selected items?"
            async def check_confirmation(confirmed: bool | None) -> None:
                if confirmed:
                    for item in list(self.selected_items):
                        _entry_type, name = item.name.split("|", 1)
                        actions.delete_item(os.path.join(self.current_dir, os.path.basename(name)))
                    self.selected_items.clear() # Clear selections after deletion
                    await self.load_directory()

            self.push_screen(ConfirmationScreen(message), check_confirmation)

        else:
            index = self.list_view.index
            if index is not None:
                selected = self.list_view.children[index]
                _, name = selected.name.split("|", 1)

                async def check_confirmation(confirmed: bool | None) -> None:
                    if confirmed:
                        actions.delete_item(os.path.join(self.current_dir, os.path.basename(name)))
                        await self.load_directory()

                self.push_screen(ConfirmationScreen(f"Delete {os.path.basename(name)}?"), check_confirmation)

    async def action_add_item(self):
        async def add_item(name: str | None) -> None:
            if name:
                actions.add_item(os.path.join(self.current_dir, name))
                await self.load_directory()

        self.push_screen(AddItemScreen(), add_item)

    async def action_toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        await self.load_directory()

    async def action_pin_item(self):
        if self.sidebar.has_focus:
            selected = self.sidebar.highlighted_child
            if selected:
                entry_type, path = selected.name.split("|", 1)
                if entry_type == "dir":
                    actions.unpin_item(path)
                    await self.update_sidebar()
        else:
            index = self.list_view.index
            if index is not None:
                selected = self.list_view.children[index]
                entry_type, name = selected.name.split("|", 1)
                if entry_type == "dir":
                    full_path = os.path.join(self.current_dir, os.path.basename(name))
                    pinned_items = [item.split("|")[0] for item in actions.get_pinned_items()]

                    if full_path in pinned_items:
                        actions.unpin_item(full_path)
                    else:
                        timestamp = os.path.getmtime(full_path)
                        actions.pin_item(full_path, os.path.basename(name), timestamp)
                    
                    await self.update_sidebar()

    async def action_toggle_focus(self):
        if self.home_sidebar.has_focus:
            self.list_view.focus()
        elif self.list_view.has_focus:
            self.sidebar.focus()
            if self.sidebar_first_focus:
                self.sidebar.index = 0
                self.sidebar_first_focus = False
        else:
            self.home_sidebar.focus()
            if self.home_sidebar_first_focus:
                self.home_sidebar.index = 0
                self.home_sidebar_first_focus = False
        
        # Update indicators after focus change
        self.update_highlight_indicators(self.list_view)
        self.update_highlight_indicators(self.home_sidebar)
        self.update_highlight_indicators(self.sidebar)

    async def update_footer_middle(self, path: str | None):
        footer_middle = self.query_one("#footer-middle", Static)
        if path and os.path.exists(path):
            stat_info = os.stat(path)
            size_bytes = stat_info.st_size
            
            if size_bytes < 1024:
                size_str = f"{size_bytes}B"
            elif size_bytes < 1024**2:
                size_str = f"{size_bytes/1024:.2f}KB"
            elif size_bytes < 1024**3:
                size_str = f"{size_bytes/1024**2:.2f}MB"
            else:
                size_str = f"{size_bytes/1024**3:.2f}GB"

            date_modified = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            permissions = stat.filemode(stat_info.st_mode)
            footer_middle.update(f"Name: {os.path.basename(path)}\nSize: {size_str} \nDate Modified: {date_modified} \nPermissions: {permissions}\n\nPress f1 for help")
        else:
            footer_middle.update("")
    async def action_toggle_footer(self):
        footer = self.query_one("#footer")
        footer.display = not footer.display


    async def update_status_bar(self):
        footer_left = self.query_one("#footer-left", Static)
        footer_middle = self.query_one("#footer-middle", Static)
        footer_right = self.query_one("#footer-right", Static)

        total_items = len(self.list_view.children)
        total, used, free = shutil.disk_usage(self.current_dir)
        
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)

        footer_left.update(f"Total Space: {total_gb:.2f} GB\nUsed Space: {used_gb:.2f} GB\nFree Space: {free_gb:.2f} GB\n\nItems: {total_items}")

        copied_items = "\n".join(actions.get_selected_items())

        footer_left.border_title = "| Stats |"
        footer_right.border_title = "| Clipboard |"
        footer_middle.border_title = "| Matadata |"

        if copied_items:
            footer_right.update(f"{copied_items}")
        else:
            footer_right.border_subtitle = ""
            footer_right.update("")

    async def action_show_keymap_help(self):
        self.push_screen(KeymapHelpScreen())

    async def action_copy_selected_items(self):
        if self.selected_items:
            items_to_write = []
            for item in self.selected_items:
                _entry_type, name = item.name.split("|", 1)
                items_to_write.append(os.path.join(self.current_dir, os.path.basename(name)))
            actions.write_selected_items(items_to_write)
            await self.action_clear_selection()

    async def action_paste_items(self):
        actions.paste_items(self.current_dir)
        await self.load_directory()
        await self.update_status_bar()

    async def action_move_items(self):
        actions.move_items(self.current_dir)
        await self.load_directory()
        await self.update_status_bar()

    async def action_rename_item(self):
        index = self.list_view.index
        if index is None:
            return
        selected = self.list_view.children[index]
        entry_type, name = selected.name.split("|", 1)
        base_name = os.path.basename(name)

        async def do_rename(new_name: str | None) -> None:
            if new_name:
                old_full_path = os.path.join(self.current_dir, base_name)
                actions.rename_item(old_full_path, new_name)
                await self.load_directory()
                await self.update_status_bar()

        self.push_screen(RenameItemScreen(base_name), do_rename)

    async def action_change_permissions(self):
        if self.selected_items:
            targets = [os.path.join(self.current_dir, os.path.basename(item.name.split("|",1)[1])) for item in self.selected_items]
        else:
            idx = self.list_view.index
            if idx is None:
                return
            targets = [os.path.join(self.current_dir, os.path.basename(self.list_view.children[idx].name.split("|",1)[1]))]

        async def apply_mode(mode: str | None) -> None:
            if mode:
                actions.change_permissions(mode, targets)
                await self.load_directory()
                await self.update_status_bar()

        self.push_screen(PermissionScreen(), apply_mode)

    async def update_home_sidebar(self):
        self.home_sidebar.clear()
    
        home_dir = os.path.expanduser("~")
        
        # Define the specific directories to show with their respective icons
        target_dirs = {
            "Home": {"path": home_dir, "icon": "\uf015"}, # fa-home
            "Downloads": {"path": os.path.join(home_dir, "Downloads"), "icon": "\uf019"}, # fa-download
            "Documents": {"path": os.path.join(home_dir, "Documents"), "icon": "\uf15c"}, # fa-file-alt
            "Pictures": {"path": os.path.join(home_dir, "Pictures"), "icon": "\uf03e"}, # fa-image
            "Videos": {"path": os.path.join(home_dir, "Videos"), "icon": "\uf03d"}, # fa-video
            "Music": {"path": os.path.join(home_dir, "Music"), "icon": "\uf001"}, # fa-music
            "Trash": {"path": os.path.join(home_dir, ".local", "share", "Trash"), "icon": "\uf1f8"} # fa-trash
        }

        for display_name, data in target_dirs.items():
            path = data["path"]
            icon = data["icon"]
            if os.path.isdir(path): # Only add if the directory actually exists
                label = Label(f"  {icon}  {display_name}")
                list_item = ListItem(
                    Horizontal(
                        Label(" ", classes="highlight-indicator"),
                        label
                    ), 
                    name=f"dir|{path}"
                )
                await self.home_sidebar.append(list_item)
        
        # Update indicators after populating
        self.update_highlight_indicators(self.home_sidebar)

    

    async def update_sidebar(self):
        self.sidebar.clear()

        pinned_items = actions.get_pinned_items()

        for item in pinned_items:
            if not item and not isinstance(item, str):
                continue

            try:
                full_path, name, timestamp = item.split("|")
                icon = "󰉋"
                list_item = ListItem(
                    Horizontal(
                        Label(" ", classes="highlight-indicator"),
                        Label(f" {icon} {name}")
                    ),
                    name=f"dir|{full_path}"
                )
                await self.sidebar.append(list_item)
            except ValueError:
                pass
        
        # Update indicators after populating
        self.update_highlight_indicators(self.sidebar)
