from parser.commands import (
    CommandValidator,
    make_command,
)
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import (
    Container,
    Grid,
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.screen import Screen
from textual.widgets import (
    Button,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    Placeholder,
    TabbedContent,
    TabPane,
)


class PanelHistory(VerticalScroll):
    BORDER_TITLE = "History"
    DEFAULT_CSS = """
    #history-list {
        background: transparent;
    }
    """

    def compose(self) -> ComposeResult:
        with ListView(id="history-list"):
            for i in range(10):
                # TODO: setup custom item component here and render it instead
                # should have step name/keyword, output data shapa, affected table??
                yield ListItem(
                    Label(f"{i}"),
                )


class PanelInput(VerticalScroll):
    DEFAULT_CSS = """
    #input-widget {
        border: round $secondary;
        background: transparent;
    }
    #input-widget.-invalid {
        border: round $error 60%;
    }
    #input-widget.-invalid:focus {
        border: round $error;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(
            id="input-widget",
            placeholder="Run your analysis",
            validate_on=["changed", "submitted"],
            valid_empty=False,
            validators=[CommandValidator()],
        )
        yield Label(id="input-validation-msg")

    @on(Input.Changed)
    def process_validation_result(self, event: Input.Changed) -> None:
        w = self.query_one("#input-validation-msg", Label)
        assert event.validation_result is not None

        # Skip error messaging for empty input
        if event.input.value == "":
            self.query_one("#input-validation-msg", Label).update("")
            return

        if not event.validation_result.is_valid:
            w.update(
                "\n".join(event.validation_result.failure_descriptions),
            )
        else:
            w.update("")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # Skip processing invalid commands
        assert event.validation_result is not None
        if not event.validation_result.is_valid:
            return

        # Skip processing empty commands
        val = event.input.value.strip()
        if len(val) == 0:
            return

        cmd = make_command(val)
        # TODO: do something if command fails??
        cmd.execute()

        output_section = self.query_ancestor("#screen").query_exactly_one("#history-list", ListView)
        output_section.append(
            ListItem(
                Label(cmd.view()),
            ),
        )
        event.input.clear()


class PanelOutput(VerticalScroll):
    def compose(self) -> ComposeResult:
        # TODO: dynamic output component based on output content??
        yield Placeholder("output", id="output-content")


class PanelPrimary(VerticalGroup):
    BORDER_TITLE = ""
    DEFAULT_CSS = """
    #input-panel {
        height: 1fr;
        margin-bottom: 1;
    }
    #output-panel {
        height: 3fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield PanelInput(id="input-panel")
        yield PanelOutput(id="output-panel")


class PanelTables(Container):
    BORDER_TITLE = "Tables"

    def compose(self) -> ComposeResult:
        with TabbedContent():
            with TabPane("Leto"):
                yield Markdown("LETO")
            with TabPane("Jessica"):
                yield Markdown("JESSICA")
            with TabPane("Paul"):
                yield Markdown("PAUL")


class PanelPlots(Container):
    BORDER_TITLE = "Plots"
    DEFAULT_CSS = """
    .plots-menu {
        height: 10%;
    }
    .plots-btn {
        background: transparent;
        border: none;
        min-width: 20%;
    }
    .plots-btn:hover,
    .plots-btn:focus,
    .plots-btn:focus-within {
        background: $background-lighten-1;
        border: none;
    }
    .plot-container {
        height: 90%;
    }
    """

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="plots-menu"):
            yield Button("<", classes="plots-btn", id="plots-menu-prev")
            yield Button(">", classes="plots-btn", id="plots-menu-next")
            yield Button("+", classes="plots-btn", id="plots-menu-zoom")
        # TODO: look into ContentSwitcher for this container
        yield Placeholder("plots", id="plot-container")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # TODO: process plot buttons
        match event.button.id:
            case "plots-menu-prev":
                pass
            case "plots-menu-prev":
                pass
            case "plots-menu-prev":
                pass
            case _:
                raise ValueError("Unsupported button id='{event.button.id}'")


class ScreenMain(Screen):
    DEFAULT_CSS = """
    Grid {
        grid-size: 3 2;
        grid-columns: 1fr 2fr 1fr;
        grid-rows: 1fr 1fr;
    }
    .panel {
        border: round $surface-lighten-3;
    }
    #history {
        row-span: 2;
    }
    #primary {
        row-span: 2;
    }
    #tables {
        row-span: 1;
    }
    #plots {
        row-span: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Grid(id="screen"):
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
