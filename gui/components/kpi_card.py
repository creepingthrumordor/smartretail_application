"""Reusable KPI card widget."""

import tkinter as tk


class KPICard(tk.Frame):
    """Show a metric title and its current value."""

    def __init__(self, master, title: str, value: str = "—", **kwargs):
        super().__init__(master, background="#2b2d42", padx=16, pady=12, **kwargs)
        self.label = tk.Label(self, text=title, fg="#b8bad0", bg="#2b2d42")
        self.label.pack(anchor="w")
        self.value = tk.Label(
            self,
            text=value,
            fg="white",
            bg="#2b2d42",
            font=("TkDefaultFont", 16, "bold"),
        )
        self.value.pack(anchor="w", pady=(6, 0))

    def set_value(self, value: str) -> None:
        self.value.configure(text=value)
