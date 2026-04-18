from textual.app import ComposeResult
from textual.containers import *
from textual.screen import *
from textual.widgets import *


class AddConfigScreen(ModalScreen[str | None]):
    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            l1 = Label("New config name:")
            l1.styles.margin = 1
            yield l1
            i1 = Input(placeholder="Type name...", id="name_input")
            i1.styles.margin = 1
            yield i1
            l2 = Label("New config path:")
            l2.styles.margin = 1
            yield l2
            i2 = Input(placeholder="Type path...", id="path_input")
            i2.styles.margin = 1
            yield i2

            with Horizontal():
                b1 = Button("Save", id="save")
                b1.styles.margin =1
                yield b1

                b2 = Button("Cancel", id="cancel")
                b2.styles.margin =1
                yield b2


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


class ConfirmScreen(ModalScreen[bool]):
    def __init__(self, title: str = "Confirm action", message: str = "Are you sure?") -> None:
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            l1 = Label(self.title)
            l1.styles.margin = 1
            yield l1
            l2 = Label(self.message)
            l2.styles.margin = 1
            yield l2

            with Horizontal():
                b1 = Button("Confirm", id="confirm")
                b1.styles.margin = 1
                yield  b1
                b2 = Button("Cancel", id="cancel")
                b2.styles.margin = 1
                yield b2

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")
