from typing import Self

import polars as pl
from textual.widgets import DataTable


class DataFrameTable(DataTable):
    """Display Polars dataframe in DataTable widget."""

    def add_df(self, df: pl.DataFrame) -> Self:
        """Add DataFrame data to DataTable."""
        self.df = df
        self.add_columns(*self._add_df_columns())
        self.add_rows(self._add_df_rows()[0:])
        return self

    def update_df(self, df: pl.DataFrame) -> None:
        """Update DataFrameTable with a new DataFrame."""
        # Clear existing datatable
        self.clear(columns=True)
        # Redraw table with new dataframe
        self.add_df(df)

    def _add_df_rows(self) -> list[tuple]:
        return self._get_df_rows()

    def _add_df_columns(self) -> tuple:
        return self._get_df_columns()

    def _get_df_rows(self) -> list[tuple]:
        """Convert dataframe rows to iterable."""
        return self.df.rows()

    def _get_df_columns(self) -> tuple:
        """Extract column names from dataframe."""
        return tuple(self.df.columns)
