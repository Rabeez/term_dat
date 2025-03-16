from dataclasses import dataclass
from enum import StrEnum, auto, unique
from pathlib import Path
from typing import Protocol

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

        keyword, *rest = value.strip().split(" ")

        try:
            keyword = Keyword[keyword.upper()]
        except KeyError:
            return self.failure(f"Invalid keyword: '{keyword}'")

        match keyword:
            case Keyword.LOAD:
                if len(rest) != 1:
                    return self.failure(
                        f"{keyword.name} only uses one argument, {len(rest)} were provided",
                    )
                filepath = Path(rest[0])

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
    def execute(self) -> None: ...


@dataclass
class CommandLoad(Command):
    path: Path

    def view(self) -> str:
        return f"LOAD {self.path.name}"

    def execute(self) -> None:
        df = pl.read_csv(self.path)


def make_command(s: str) -> Command:
    keyword, *rest = s.strip().split(" ")
    keyword = Keyword[keyword.upper()]
    match keyword:
        case Keyword.LOAD:
            filepath = Path(rest[0])
            return CommandLoad(filepath)
