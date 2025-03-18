from parser.commands import (
    Command,
    CommandLoad,
    CommandPlot,
    CommandValidator,
    make_command,
)
from pathlib import Path

import polars as pl
from textual import on
from textual.app import App, ComposeResult
from textual.containers import (
    Container,
    Grid,
    HorizontalGroup,
    VerticalGroup,
    VerticalScroll,
)
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    ContentSwitcher,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    TabbedContent,
    TabPane,
)
from textual_plotext import PlotextPlot

from components.dataframe import DataFrameTable
from components.modal import ModalOverlay


class PanelHistory(VerticalScroll):
    BORDER_TITLE = "History"
    DEFAULT_CSS = """
    #history-list {
        background: transparent;
    }
    """

    history: reactive[list[Command]] = reactive([], recompose=True)

    def compose(self) -> ComposeResult:
        with ListView(id="history-list"):
            for step in self.history:
                yield ListItem(step.as_widget())


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
            w.update("\n".join(event.validation_result.failure_descriptions))
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

        log_msg = None
        match cmd:
            case CommandLoad():
                name, table = cmd.execute()

                # Append to reactive list in tables panel, and trigger reactive updates
                tables_list = self.query_ancestor("#screen").query_exactly_one(
                    "#tables",
                    PanelTables,
                )
                # NOTE: will overwrite older table variables if same name is used
                tables_list.tables[name] = table
                tables_list.mutate_reactive(PanelTables.tables)

                log_msg = cmd.as_log(f"Created new dataframe of shape={table.shape}")
            case CommandPlot():
                # Grab relevant dataframe cols etc
                tables_list = self.query_ancestor("#screen").query_exactly_one(
                    "#tables",
                    PanelTables,
                )
                data = tables_list.tables[cmd.table_name]
                newplot = cmd.execute(data)

                # Append to reactive list in history panel, and trigger reactive updates
                plots_list = self.query_ancestor("#screen").query_exactly_one("#plots", PanelPlots)
                new_plot_idx = len(plots_list.plots)
                newplot.id = f"plot_idx_{new_plot_idx}"
                plots_list.plots.append(newplot)
                plots_list.mutate_reactive(PanelPlots.plots)
                # Always show the latest plot
                plots_list.visible_plot_idx = new_plot_idx

                log_msg = cmd.as_log(f"Created new plot at index {new_plot_idx}")

        # Append to reactive list in history panel, and trigger reactive updates
        tables_list = self.query_ancestor("#screen").query_exactly_one("#history", PanelHistory)
        tables_list.history.append(cmd)
        tables_list.mutate_reactive(PanelHistory.history)

        # Append to logs
        primary_panel = self.query_ancestor("#screen").query_exactly_one("#primary", PanelPrimary)
        primary_panel.logs.append(Markdown(log_msg, classes="log-msg"))
        primary_panel.mutate_reactive(PanelPrimary.logs)

        # Clear input box
        event.input.clear()


class PanelPrimary(VerticalGroup):
    DEFAULT_CSS = """
    #input-panel {
        height: 1fr;
        margin-bottom: 1;
    }
    #logs-content {
        height: 3fr;
        background: transparent;
        border: round $surface-lighten-3;
    }
    .log-msg {
        background: transparent;
        border-bottom: $surface-lighten-1;
    }
    """

    logs: reactive[list[Markdown]] = reactive([], recompose=True)

    def compose(self) -> ComposeResult:
        yield PanelInput(id="input-panel")
        log_container = VerticalScroll(id="logs-content")
        log_container.border_title = "Logs"
        with log_container:
            # Display logs, latest on top
            yield from reversed(self.logs)


class PanelTables(Container):
    BORDER_TITLE = "Tables"

    tables: reactive[dict[str, pl.DataFrame]] = reactive({}, recompose=True)

    def compose(self) -> ComposeResult:
        # TODO: add 'zoom' button to open datatable in float view
        # TODO: add zoom to logs
        with TabbedContent(disabled=len(self.tables) == 0):
            for name, table in self.tables.items():
                with TabPane(name):
                    yield DataFrameTable().add_df(table)


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

    plots: reactive[list[PlotextPlot]] = reactive([], recompose=True)
    visible_plot_idx: reactive[int | None] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        with HorizontalGroup(id="plots-menu"):
            yield Button(
                "󰒮",
                classes="plots-btn",
                id="plots-menu-prev",
                disabled=(
                    (self.visible_plot_idx is None)
                    or (self.visible_plot_idx is not None and self.visible_plot_idx == 0)
                ),
            )
            yield Button(
                "󰒭",
                classes="plots-btn",
                id="plots-menu-next",
                disabled=(
                    (self.visible_plot_idx is None)
                    or (
                        self.visible_plot_idx is not None
                        and self.visible_plot_idx == len(self.plots) - 1
                    )
                ),
            )
            yield Button(
                "",
                classes="plots-btn",
                id="plots-menu-zoom",
                disabled=(self.visible_plot_idx is None),
            )
            if self.visible_plot_idx is not None:
                yield Label(f"Plot {self.visible_plot_idx}")

        with ContentSwitcher(
            initial=f"plot_idx_{self.visible_plot_idx}"
            if self.visible_plot_idx is not None
            else None,
        ):
            yield from self.plots

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # TODO: add navigation/zoom to logs
        if self.visible_plot_idx is None:
            return
        match event.button.id:
            case "plots-menu-prev":
                self.visible_plot_idx -= 1
            case "plots-menu-next":
                self.visible_plot_idx += 1
            case "plots-menu-zoom":
                self.app.push_screen(
                    ModalOverlay(
                        Label(f"Plot {self.visible_plot_idx}"),
                        self.plots[self.visible_plot_idx],
                    ),
                )
            case _:
                raise ValueError(f"Unsupported button id='{event.button.id}'")


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
        border: none;
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
