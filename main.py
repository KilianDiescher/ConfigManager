import shlex
import shutil
import subprocess

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Input, Button
import json
from textual.screen import ModalScreen
from textual.containers import Vertical
import os

class ConfigManager(App):

    BINDINGS = [("enter", "select_cursor", "Select"),
                ("ctrl+a", "config_add", "Add new config"),
                ("ctrl+d", "config_rm", "Delete config")
                ]

    def on_mount(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(base_dir,"configs.json")):
            self.configs: dict[str, str] = self.load_configs()
        else:
            self.configs: dict[str, str] = {}

        self.selection_mode = "select"
        self.update_list()
        self.refresh_status()

    def compose(self) -> ComposeResult:
        items = []

        yield Header()

        yield ListView(*items,id="configs")

        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        name = getattr(event.item, "data", None)
        if not name:
            self.notify("No selection data")
            return
        path = self.configs.get(name, "<unknown path>")
        self.notify(f"Selected: {name} -> {path}")

        if self.selection_mode == "select":
            self.open_in_editor(name)
        elif self.selection_mode  == "delete":
            self.configs.pop(name)
            self.selection_mode = "select"

        self.update_list()
        self.refresh_status()


    def open_in_editor(self,name):
        abs_path = os.path.abspath(self.configs[name])
        terminal = self.get_terminal()

        editor_cmd = f"nano {shlex.quote(abs_path)}"
        term_name = os.path.basename(self.get_terminal())

        if term_name in {"kitty", "foot"}:
            subprocess.Popen([terminal, "bash", "-lc", editor_cmd])
        elif term_name in  {"alacritty","konsole"} :
            subprocess.Popen([terminal, "-e", "bash", "-lc", editor_cmd])
        elif term_name == "wezterm":
            subprocess.Popen([terminal, "start", "--", "bash", "-lc", editor_cmd])
        else:
            self.notify(f"Unsupported terminal: {term_name}")
            return


    def get_terminal(self):
        terminal = (
                shutil.which("kitty")
                or shutil.which("foot")
                or shutil.which("alacritty")
                or shutil.which("wezterm")
                or shutil.which("konsole")
        )
        if not terminal:
            raise RuntimeError("No supported terminal found \(kitty/foot/alacritty/wezterm\)")

        return terminal

    def action_config_add(self) -> None:
        self.push_screen(AddConfigScreen(), self._on_new_config)

    def _on_new_config(self, value: str | None) -> None:
        if not value:
            self.notify("Cancelled")
            return


        self.configs[value[0]] = value[1]
        self.notify(f"Added: {value[0]} with path {value[1]}")
        self.update_list()

    def action_config_rm(self) -> None:

        if not self.selection_mode == "delete":
            self.selection_mode = "delete"
        else :
            self.selection_mode = "select"

        self.refresh_status()

    def refresh_status(self) -> None:
        mode = self.selection_mode
        self.sub_title = f"{mode}"



    def update_list(self):
        list_view = self.query_one("#configs", ListView)
        list_view.clear()
        for key in self.configs:
            item = ListItem(Label(key))
            item.data = key
            list_view.append(item)

        self.save_configs()

    def save_configs(self):
        with open("configs.json","w") as file:
            json.dump(self.configs,file)

    def load_configs(self):
        with open("configs.json","r") as file:
            return json.load(file)



class AddConfigScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("New config name:")
            yield Input(placeholder="Type name...", id="name_input")
            yield Label("New config path:")
            yield Input(placeholder="Type path...", id="path_input")
            yield Button("Save", id="save")
            yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#name_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            name = self.query_one("#name_input", Input).value.strip()
            path = self.query_one("#path_input", Input).value.strip()
            result = [name,path]
            self.dismiss(result or None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = self.query_one("#name_input", Input).value.strip()
        path = self.query_one("#path_input", Input).value.strip()
        result = [name, path]
        self.dismiss(result or None)

def run() -> None:
    ConfigManager().run()


if __name__ == "__main__":
    run()

