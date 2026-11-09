"""Fallback chart component for displaying result summaries."""

import tkinter as tk


class ChartView(tk.Frame):
    """Basic text view used when no embedded chart is available."""

    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#1e1e24", **kwargs)
        self.label = tk.Label(
            self,
            text="Run an analysis to view charts and tables.",
            fg="white",
            bg="#1e1e24",
        )
        self.label.pack(anchor="nw", padx=16, pady=16)

    def show_result(self, result) -> None:
        self.label.configure(
            text=(
                f"{result.strategy_name}\n\n"
                f"{result.summary}\n\n"
                f"{result.tables}"
            )
        )
