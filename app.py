from pathlib import Path

from textual import on
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
            validators=[
                CommandValidator(),
            ],
        )
        yield Label(id="input-validation-msg")

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        assert event.validation_result is not None
        if not event.validation_result.is_valid:
            self.query_one("#input-validation-msg", Label).update(
                "\n".join(event.validation_result.failure_descriptions),
            )
        else:
            self.query_one("#input-validation-msg", Label).update("")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        # TODO: validation should return before submit event
        # validation should return parsed object for different commands
        # use command.to_str() method to render in history (or to_listitem())
        # call command.execute() method at end of this method here

        assert event.validation_result is not None
        if not event.validation_result.is_valid:
            return

        val = event.input.value.strip()
        if len(val) == 0:
            return

        output_section = self.query_ancestor("#screen").query_exactly_one("#history-list", ListView)
        output_section.append(
            ListItem(
                Label(val),
            ),
        )
        event.input.clear()


class PanelOutput(VerticalScroll):
    def compose(self) -> ComposeResult:
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
        border: round $surface-lighten-3;
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
