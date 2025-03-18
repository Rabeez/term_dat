from dataclasses import dataclass
from enum import StrEnum, auto, unique
from pathlib import Path
import time
from typing import Any, Protocol

import polars as pl
from textual.validation import ValidationResult, Validator
from textual.widget import Widget
from textual.widgets import Label
from textual_plotext import PlotextPlot


@unique
class Keyword(StrEnum):
    LOAD = auto()
    PLOT = auto()


class CommandValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        # Ensure empty entry is valid, for nicer UI look
        if value.strip() == "":
            return self.success()

        try:
            keyword, rest = value.strip().split(" ", 1)
        except ValueError:
            return self.failure("Invalid syntax")

        try:
            keyword = Keyword[keyword.upper()]
        except KeyError:
            return self.failure(f"Invalid keyword: '{keyword}'")

        # TODO: improve validation logic by passing current app state
        # -> to validate table names
        # -> to validate column names (and types?)

        match keyword:
            case Keyword.LOAD:
                try:
                    table_name, filepath = CommandLoad.preprocess(rest)
                except ValueError:
                    return self.failure(f"Invalid arguments for '{keyword}': {rest}")

                if len(table_name) <= 0:
                    return self.failure("Table name is required")

                if not filepath.exists():
                    return self.failure(f"Provided path does not exist: '{filepath}'")

                if not filepath.is_file():
                    return self.failure(f"Provided path is not a file: '{filepath}'")

                if filepath.suffix != ".csv":
                    return self.failure(
                        f"Can only load CSV files, you provided a '{filepath.suffix}' file",
                    )
            case Keyword.PLOT:
                try:
                    plot_kind, table_name, *args = CommandLoad.preprocess(rest)
                except ValueError:
                    return self.failure(f"Invalid arguments for '{keyword}': {rest}")

                try:
                    plot_kind = PlotKind[plot_kind.upper()]
                except KeyError:
                    return self.failure(f"Invalid PlotKind: '{plot_kind}'")

        return self.success()


class Command(Protocol):
    raw: str

    def as_widget(self) -> Widget: ...
    def as_log(self, msg: str) -> str:
        return f"**{time.strftime('%Y-%m-%d %H:%M:%S')}**\n\n" + f"`{self.raw}`\n\n" + msg

    @staticmethod
    def preprocess(args: str) -> list[Any]: ...
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...  # noqa: ANN401


@dataclass
class CommandLoad(Command):
    raw: str
    table_name: str
    path: Path

    def as_widget(self) -> Widget:
        return Label(f'LOAD {self.table_name}="{self.path.name}"')

    @staticmethod
    def preprocess(args: str) -> list[Any]:
        table_name, rest = args.split(" ", 1)
        # NOTE: Remove enclosing double quotes
        # Path will always be created so we check the requirements manually
        filepath = rest[1:-1]
        return [
            table_name,
            Path(filepath),
        ]

    def execute(self) -> tuple[str, pl.DataFrame]:
        table = pl.read_csv(self.path)
        # TODO: clean column names here, no spaces
        return (
            self.table_name,
            table,
        )


@unique
class PlotKind(StrEnum):
    SCATTER = auto()
    LINE = auto()


@dataclass
class CommandPlot(Command):
    raw: str
    kind: str
    table_name: str
    col_x: str
    col_y: str

    def as_widget(self) -> Widget:
        return Label(f"PLOT {self.kind} {self.table_name}")

    @staticmethod
    def preprocess(args: str) -> list[Any]:
        plot_kind, rest = args.split(" ", 1)
        table_name, rest = rest.split(" ", 1)
        col_x, col_y = rest.split(" ", 1)
        return [
            plot_kind,
            table_name,
            col_x,
            col_y,
        ]

    def execute(self, data: pl.DataFrame) -> PlotextPlot:
        x_vals = data.select(self.col_x).to_series().to_list()
        y_vals = data.select(self.col_y).to_series().to_list()

        newplot = PlotextPlot()
        match self.kind:
            case PlotKind.SCATTER:
                newplot.plt.scatter(x_vals, y_vals)
            case PlotKind.LINE:
                newplot.plt.plot(x_vals, y_vals)

        return newplot


def make_command(s: str) -> Command:
    keyword, rest = s.strip().split(" ", 1)
    keyword = Keyword[keyword.upper()]
    match keyword:
        case Keyword.LOAD:
            table_name, filepath = CommandLoad.preprocess(rest)
            return CommandLoad(s, table_name, filepath)
        case Keyword.PLOT:
            plot_kind, table_name, col_x, col_y = CommandPlot.preprocess(rest)
            return CommandPlot(s, plot_kind, table_name, col_x, col_y)
