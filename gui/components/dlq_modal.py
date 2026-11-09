"""Searchable inspector for quarantined source rows."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from smartretail.validation.dead_letter_queue import DeadLetterQueue


class DLQWindow(tk.Toplevel):
    """Display and export dead-letter queue entries."""

    def __init__(self, master, queue: DeadLetterQueue):
        super().__init__(master)
        self.title("Dead-Letter Queue")
        self.geometry("850x450")
        self.queue = queue
        self.search = tk.StringVar()

        entry = ttk.Entry(self, textvariable=self.search)
        entry.pack(fill="x", padx=10, pady=10)
        self.table = ttk.Treeview(
            self,
            columns=("row", "reason", "source", "raw"),
            show="headings",
        )
        self.table.pack(fill="both", expand=True, padx=10)
        for column in ("row", "reason", "source", "raw"):
            self.table.heading(column, text=column)

        self.search.trace_add("write", lambda *_args: self.refresh())
        ttk.Button(
            self,
            text="Export DLQ to CSV",
            command=self.export,
        ).pack(pady=8)
        self.refresh()

    def refresh(self) -> None:
        self.table.delete(*self.table.get_children())
        term = self.search.get().lower()
        for record in self.queue.get_all():
            if term in record.reason.lower():
                self.table.insert(
                    "",
                    "end",
                    values=(
                        record.line_number,
                        record.reason,
                        record.source,
                        record.raw_data[:150],
                    ),
                )

    def export(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        try:
            self.queue.export_csv(path)
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc))
