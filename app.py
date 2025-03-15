from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Grid, VerticalGroup, VerticalScroll
from textual.screen import Screen
from textual.validation import ValidationResult, Validator
from textual.widgets import Input, Label, ListItem, ListView, Placeholder


class PanelHistory(VerticalScroll):
    BORDER_TITLE = "History"

    def compose(self) -> ComposeResult:
        with ListView(id="history-list"):
            for i in range(10):
                yield ListItem(
                    Label(f"{i}"),
                )


class CommandValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if self.is_palindrome(value):
            return self.success()
        else:
            return self.failure("That's not a palindrome :(")

    @staticmethod
    def is_palindrome(value: str) -> bool:
        return value == value[::-1]


class CommandInput(Input):
    DEFAULT_CSS = """
    Input.-valid {
        border: round $success 60%;
    }
    Input.-valid:focus {
        border: round $success;
    }
    """

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Run your analysis",
            validate_on=["changed"],
            validators=[
                CommandValidator(),
            ],
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # TODO: validation should return before submit event
        # validation should return parsed object for different commands
        # use command.to_str() method to render in history (or to_listitem())
        # call command.execute() method at end of this method here
        output_section = self.query_ancestor("#screen").query_exactly_one("#history-list", ListView)
        output_section.append(
            ListItem(
                Label(self.query_exactly_one(Input).value),
            ),
        )


class PanelInput(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield CommandInput()


class PanelOutput(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Placeholder("output", id="output-content")


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
