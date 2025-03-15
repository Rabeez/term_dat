from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Grid, VerticalGroup, VerticalScroll
from textual.screen import Screen
from textual.widgets import Placeholder


class PanelHistory(VerticalScroll):
    BORDER_TITLE = "History"

    def compose(self) -> ComposeResult:
        yield Placeholder("History")


class PanelInput(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Placeholder("input")


class PanelOutput(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Placeholder("output")


class PanelPrimary(VerticalGroup):
    BORDER_TITLE = ""
    DEFAULT_CSS = """
    #input-section {
        height: 1fr;
        margin-bottom: 1;
    }
    #output-section {
        height: 3fr;
    }

    """

    def compose(self) -> ComposeResult:
        yield PanelInput(id="input-section")
        yield PanelOutput(id="output-section")


class PanelTables(VerticalScroll):
    BORDER_TITLE = "Tables"

    def compose(self) -> ComposeResult:
        yield Placeholder("tables")


class PanelPlots(VerticalScroll):
    BORDER_TITLE = "Plots"

    def compose(self) -> ComposeResult:
        yield Placeholder("plots")


class ScreenMain(Screen):
    DEFAULT_CSS = """
    Grid {
        grid-size: 3 2;
        grid-columns: 1fr 2fr 1fr;
        grid-rows: 1fr 1fr;
    }
    .panel {
        border: round;
    }
    #history {
        row-span: 2;
    }
    #primary {
        row-span: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Grid():
            yield PanelHistory(id="history", classes="panel")
            yield PanelPrimary(id="primary", classes="panel")
            yield PanelTables(id="tables", classes="panel")
            yield PanelPlots(id="plots", classes="panel")


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
        self.push_screen(ScreenMain())

    def import_script(self, script: Path) -> None:
        with open(script, "r") as f:
            for line in f:
                print(f"Executing: {line.strip()}")  # Process REPL logic
