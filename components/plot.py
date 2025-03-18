from parser.base import Command

from textual.widget import Widget
from textual_plotext import PlotextPlot


class Plot(Widget):
    def __init__(self, plot: PlotextPlot, cmd: Command) -> None:
        """TODO:"""
        super().__init__()
        self.plot = plot
        self.cmd = cmd
