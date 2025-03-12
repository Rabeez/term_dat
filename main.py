from pathlib import Path
from typing import Annotated

import typer

from app import TUIApp


# TODO: use strenum here for plot options
def main(
    script: Annotated[
        Path | None,
        typer.Option("--script", "-s", help="Path to script file for execution"),
    ] = None,
    plot: Annotated[
        str,
        typer.Option("--plot", "-p", help="Plot mode: 'ascii' (default) or 'window'"),
    ] = "ascii",
) -> None:
    """Start the TUI application with optional script execution and plot mode."""
    if plot not in ["ascii", "window"]:
        typer.echo("Invalid plot option. Choose 'ascii' or 'window'.", err=True)
        raise typer.Exit(code=1)

    tui_app = TUIApp(
        script=script,
        plot_mode=plot,
    )
    tui_app.run()


if __name__ == "__main__":
    typer.run(main)
