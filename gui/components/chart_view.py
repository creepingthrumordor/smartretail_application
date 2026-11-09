import tkinter as tk
class ChartView(tk.Frame):
 def __init__(self,master,**kw):super().__init__(master,bg='#1e1e24',**kw);self.label=tk.Label(self,text='Run an analysis to view charts and tables.',fg='white',bg='#1e1e24');self.label.pack(anchor='nw',padx=16,pady=16)
 def show_result(self,result):self.label.configure(text=f"{result.strategy_name}\n\n{result.summary}\n\n{result.tables}")
