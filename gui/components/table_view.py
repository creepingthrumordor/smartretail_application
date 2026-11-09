"""Reusable table widget for displaying analytics rows."""

from tkinter import ttk
from typing import Any


class TableView(ttk.Treeview):
    """Populate a heading-based tree view from dictionary rows."""

    def show_rows(self, rows: list[dict[str, Any]]) -> None:
        self.delete(*self.get_children())
        if not rows:
            return

        columns = list(rows[0])
        self.configure(columns=columns, show="headings")
        for column in columns:
            self.heading(column, text=column)
            self.column(column, width=150)
        for row in rows:
            self.insert("", "end", values=[row.get(column, "") for column in columns])
