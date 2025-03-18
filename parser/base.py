import time
from typing import Any, Protocol

from textual.widget import Widget


class Command(Protocol):
    raw: str

    def as_widget(self) -> Widget: ...
    def as_log(self, msg: str) -> str:
        return f"**{time.strftime('%Y-%m-%d %H:%M:%S')}**\n\n" + f"`{self.raw}`\n\n" + msg

    @staticmethod
    def preprocess(args: str) -> list[Any]: ...
    def execute(self, *args: Any, **kwargs: Any) -> Any: ...  # noqa: ANN401
