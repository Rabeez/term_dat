from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import HorizontalScroll, VerticalScroll
from textual.screen import Screen
from textual.widgets import Placeholder


class Header(Placeholder):
    DEFAULT_CSS = """
    Header {
        height: 3;
        dock: top;
    }
    """


class Footer(Placeholder):
    DEFAULT_CSS = """
    Footer {
        height: 3;
        dock: bottom;
    }
    """


class Tweet(Placeholder):
    DEFAULT_CSS = """
    Tweet {
        height: 5;
        width: 1fr;
        border: tall $background;
    }
    """


class Column(VerticalScroll):
    DEFAULT_CSS = """
    Column {
        height: 1fr;
        width: 32;
        margin: 0 2;
    }
    """

    def compose(self) -> ComposeResult:
        for tweet_no in range(1, 20):
            yield Tweet(id=f"Tweet{tweet_no}")


class TweetScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Footer(id="Footer")
        with HorizontalScroll():
            yield Column()
            yield Column()
            yield Column()
            yield Column()


class TUIApp(App):
    def __init__(
        self,
        script: Path | None = None,
        plot_mode: str = "ascii",
    ) -> None:
        """TODO:"""
        super().__init__()
        self.script = script
        self.plot_mode = plot_mode

        if self.script is not None:
            raise ValueError("NOT IMPLEMENTED")
        if self.plot_mode != "ascii":
            raise ValueError("NOT IMPLEMENTED")

    def on_mount(self) -> None:
        if self.script:
            self.import_script(self.script)

    def on_ready(self) -> None:
        self.push_screen(TweetScreen())

    def import_script(self, script: Path) -> None:
        with open(script, "r") as f:
            for line in f:
                print(f"Executing: {line.strip()}")  # Process REPL logic
