import tkinter as tk
from tkinter import ttk,filedialog,messagebox
class DLQWindow(tk.Toplevel):
 def __init__(self,master,queue):
  super().__init__(master);self.title('Dead-Letter Queue');self.geometry('850x450');self.queue=queue
  self.search=tk.StringVar();entry=ttk.Entry(self,textvariable=self.search);entry.pack(fill='x',padx=10,pady=10);self.table=ttk.Treeview(self,columns=('row','reason','source','raw'),show='headings');self.table.pack(fill='both',expand=True,padx=10)
  for c in ('row','reason','source','raw'):self.table.heading(c,text=c)
  self.search.trace_add('write',lambda *_:self.refresh());ttk.Button(self,text='Export DLQ to CSV',command=self.export).pack(pady=8);self.refresh()
 def refresh(self):
  self.table.delete(*self.table.get_children());term=self.search.get().lower()
  for x in self.queue.get_all():
   if term in x.reason.lower():self.table.insert('','end',values=(x.line_number,x.reason,x.source,x.raw_data[:150]))
 def export(self):
  path=filedialog.asksaveasfilename(defaultextension='.csv')
  if path:
   try:self.queue.export_csv(path)
   except OSError as e:messagebox.showerror('Export failed',str(e))
