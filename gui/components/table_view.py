import tkinter as tk
from tkinter import ttk
class TableView(ttk.Treeview):
 def show_rows(self,rows):
  self.delete(*self.get_children())
  if not rows:return
  cols=list(rows[0]);self.configure(columns=cols,show='headings')
  for c in cols:self.heading(c,text=c);self.column(c,width=150)
  for row in rows:self.insert('', 'end',values=[row.get(c,'') for c in cols])
