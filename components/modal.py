from textual import events
from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.screen import Screen
from textual.widget import Widget


class ModalOverlay(Screen):
    DEFAULT_CSS = """
    ModalOverlay {
        align: center middle;
        background: $background 85%;
    }
    #overlay {
        width: 90%;
        height: 90%;
        border: round $surface-lighten-3;
    }
    """

    def __init__(self, *content: Widget) -> None:
        """A floating modal overlay with `content` arranged vertically"""
        super().__init__()
        self.content = content

    def compose(self) -> ComposeResult:
        with VerticalGroup(id="overlay", classes="modal-overlay"):
            yield from self.content

    def on_key(self, event: events.Key) -> None:
        if event.character == "q":
            self.app.pop_screen()
