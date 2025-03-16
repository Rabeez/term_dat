from dataclasses import dataclass
from enum import StrEnum, auto, unique
from pathlib import Path
from typing import Any, Protocol

import polars as pl
from textual.validation import ValidationResult, Validator


@unique
class Keyword(StrEnum):
    LOAD = auto()


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

        match keyword:
            case Keyword.LOAD:
                try:
                    table_name, filepath = CommandLoad.preprocess(rest)
                except ValueError:
                    return self.failure(f"Invalid arguments for '{keyword}': {rest}")

                if len(table_name) <= 0:
                    return self.failure("Invalid table name provided")

                if not filepath.exists():
                    return self.failure(f"Provided path does not exist: '{filepath}'")

                if not filepath.is_file():
                    return self.failure(f"Provided path is not a file: '{filepath}'")

                if filepath.suffix != ".csv":
                    return self.failure(
                        f"Can only load CSV files, you provided a '{filepath.suffix}' file",
                    )

        return self.success()


class Command(Protocol):
    def view(self) -> str: ...
    @staticmethod
    def preprocess(args: str) -> list[Any]: ...
    def execute(self) -> None: ...


@dataclass
class CommandLoad(Command):
    table_name: str
    path: Path

    def view(self) -> str:
        # TODO: this should return a widget that can be put inside a ListItem
        return f'LOAD {self.table_name}="{self.path.name}"'

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

    def execute(self) -> None:
        # TODO: need to update global app state here
        _ = pl.read_csv(self.path)


def make_command(s: str) -> Command:
    keyword, rest = s.strip().split(" ", 1)
    keyword = Keyword[keyword.upper()]
    match keyword:
        case Keyword.LOAD:
            table_name, filepath = CommandLoad.preprocess(rest)
            return CommandLoad(table_name, filepath)
