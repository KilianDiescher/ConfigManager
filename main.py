import shlex
import shutil
import subprocess
from AddConfigScreen import AddConfigScreen, ConfirmScreen
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label, Input, Button, TextArea
import json
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
import os

class ConfigManager(App):

    BINDINGS = [("enter", "select_cursor", "Select"),
                ("ctrl+a", "config_add", "Add new config"),
                ("ctrl+d", "config_rm", "Remove config"),
                ("ctrl+o", "config_save", "Save config"),
                ("ctrl+e", "config_open", "Open in external editor"),
                ]

    def on_mount(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(base_dir, "configs.json")

        if os.path.exists(self.config_path):
            self.configs: dict[str, str] = self.load_configs()
        else:
            self.configs = {}

        self.selection_mode = "select"
        self.selection = ""
        self.update_list()
        self.refresh_status()

    def compose(self) -> ComposeResult:
        items = []

        yield Header()

        with Horizontal():

            yield ListView(*items,id="configs")
            yield TextArea.code_editor(language="python",id="editor")

        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        name = getattr(event.item, "data", None)
        if not name:
            self.notify("No selection data")
            return

        if self.selection_mode == "select":
            # self.open_in_ceditor(name)
            self.selection = name
            self.open_in_editor(name)

        elif self.selection_mode  == "delete":
            self.configs.pop(name)
            self.selection_mode = "select"

        self.update_list()
        self.refresh_status()

    def open_in_editor(self, name):
        path = self.configs.get(name, "<unknown path>")
        Text = ""
        with open(path,"r") as conf:
            Text = conf.read()

        editor = self.query_one("#editor", TextArea)
        editor.text = Text

    def action_config_save(self):
        if not self.selection:
            self.notify("Select a config first")
            return

        path = self.configs.get(self.selection)
        if not path:
            self.notify("No path selected")
            return

        msg = f"Are you sure you want to write all changes to\n{path}?"
        self.push_screen(ConfirmScreen(message=msg), self._on_save_confirmed)

    def _on_save_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            self.notify("Cancelled")
            return

        path = self.configs.get(self.selection)
        if not path:
            self.notify("No path selected")
            return

        text = self.query_one("#editor", TextArea).text
        with open(path, "w", encoding="utf-8") as file:
            file.write(text)
        self.notify(f"Saved: {self.selection}")

    def open_in_ceditor(self,name):
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

    def action_config_open(self):
        if not self.selection:
            self.notify("Select a config first")
            return
        self.open_in_ceditor(self.selection)

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

        name = value[0].strip()
        path = value[1].strip()
        if not name or not path:
            self.notify("Name and path are required")
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
        tmp_path = f"{self.config_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(self.configs, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(tmp_path, self.config_path)

    def load_configs(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
            return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


def run() -> None:
    ConfigManager().run()


if __name__ == "__main__":
    run()

