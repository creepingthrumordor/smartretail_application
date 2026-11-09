"""Tk dashboard for SmartRetail analytics."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from pathlib import Path
from decimal import Decimal

from smartretail.config import ANALYSES
from smartretail.services.facade import SmartRetailFacade
from .components.dlq_modal import DLQWindow

# Warm dark palette sampled from the reference screenshot.
BG = '#1C180F'
PANEL = '#322A1C'
MUTED = '#A89B81'
DARK = '#E8DDC4'       # foreground text
ACCENT = '#F99F46'
TEAL = '#B69A63'
CORAL = '#E77D4A'
GOLD = '#F99F46'
LAVENDER = '#B9AA87'
SLATE = '#493E2B'

class RoundedSurface(tk.Frame):
    """Canvas-backed material surface with a subtle drop shadow."""
    def __init__(self,master,color=PANEL,radius=14,inset=14,**kwargs):
        super().__init__(master,bg=master.cget('bg'),bd=0,highlightthickness=0,**kwargs)
        self.fill=color;self.radius=radius;self.inset=inset
        self.canvas=tk.Canvas(self,bg=master.cget('bg'),highlightthickness=0,bd=0)
        self.canvas.place(x=0,y=0,relwidth=1,relheight=1)
        self.shadow=self.canvas.create_polygon(0,0,0,0,smooth=True,splinesteps=20,fill='#15120C',outline='')
        self.shape=self.canvas.create_polygon(0,0,0,0,smooth=True,splinesteps=20,fill=color,outline='')
        self.content=tk.Frame(self,bg=color,bd=0,highlightthickness=0)
        self.window=self.canvas.create_window(inset,inset,anchor='nw',window=self.content)
        self.bind('<Configure>',self._resize)
    def _rounded_points(self,width,height,offset=0):
        r=min(self.radius,max(2,(height-2*offset)/2));x0=y0=offset;x1=width-offset;y1=height-offset
        return [x0+r,y0,x1-r,y0,x1,y0,x1,y0+r,x1,y1-r,x1,y1,x1-r,y1,x0+r,y1,x0,y1,x0,y1-r,x0,y0+r,x0,y0]
    def _resize(self,event):
        if event.width<3 or event.height<3:return
        self.canvas.coords(self.shadow,*self._rounded_points(event.width,event.height,2))
        self.canvas.coords(self.shape,*self._rounded_points(event.width,event.height,0))
        self.canvas.coords(self.window,self.inset,self.inset)
        self.canvas.itemconfigure(self.window,width=max(1,event.width-2*self.inset),height=max(1,event.height-2*self.inset))

class MaterialButton(tk.Canvas):
    """Rounded, borderless button with restrained material-style feedback."""
    def __init__(self,master,text,command,fill,foreground=DARK,height=42):
        super().__init__(master,height=height,bg=master.cget('bg'),highlightthickness=0,bd=0,cursor='hand2')
        self.text=text;self.command=command;self.base=fill;self.current=fill;self.foreground=foreground;self.height=height
        self.bind('<Configure>',self._draw);self.bind('<Button-1>',self._click)
        self.bind('<Enter>',lambda _event:self._set_fill(GOLD if self.base==ACCENT else '#5A4A32'))
        self.bind('<Leave>',lambda _event:self._set_fill(self.base))
    def _click(self,_event):self.command()
    def _set_fill(self,color):self.current=color;self._draw()
    def _draw(self,_event=None):
        self.delete('all');w=max(self.winfo_width(),100);h=self.height;r=11
        points=[r,0,w-r,0,w,0,w,r,w,h-r,w,h,w-r,h,r,h,0,h,0,h-r,0,r,0,0]
        self.create_polygon(*points,smooth=True,splinesteps=20,fill=self.current,outline=self.current)
        self.create_text(14,h/2,text=self.text,anchor='w',fill=self.foreground,font=('TkDefaultFont',10,'bold'))

class DashboardWindow:
    def __init__(self, facade=None):
        self.facade = facade or SmartRetailFacade()
        self.root = tk.Tk()
        self.root.title('SmartRetail Analytics • Enterprise')
        self.root.geometry('1440x900')
        self.root.minsize(1050, 700)
        self.root.configure(bg=BG)
        self.path = tk.StringVar()
        self.analysis = tk.StringVar(value=ANALYSES[0])
        self.status = tk.StringVar(value='Select a dataset and run an analysis.')
        self._build()

    def _build(self):
        self.root.option_add('*Font', 'TkDefaultFont 10')
        style=ttk.Style(self.root)
        try: style.theme_use('clam')
        except tk.TclError: pass
        style.configure('TCombobox',fieldbackground=PANEL,background=SLATE,foreground=DARK,arrowcolor=DARK,
                        bordercolor=SLATE,lightcolor=SLATE,darkcolor=SLATE,relief='flat',borderwidth=0)
        style.map('TCombobox',fieldbackground=[('readonly',PANEL)],foreground=[('readonly',DARK)],
                  bordercolor=[('focus',ACCENT),('!focus',SLATE)],lightcolor=[('focus',ACCENT),('!focus',SLATE)],
                  darkcolor=[('focus',ACCENT),('!focus',SLATE)])
        style.configure('Treeview',background='#292216',fieldbackground='#292216',foreground=DARK,rowheight=26,borderwidth=0)
        style.configure('Treeview.Heading',background=SLATE,foreground=DARK,relief='flat')
        style.map('Treeview',background=[('selected','#5E472D')])
        style.configure('Horizontal.TProgressbar',troughcolor='#403624',background=ACCENT,bordercolor='#403624',lightcolor=ACCENT,darkcolor=ACCENT)
        side = tk.Frame(self.root, bg='#211C12', width=260, padx=18, pady=22)
        side.pack(side='left', fill='y'); side.pack_propagate(False)
        tk.Label(side, text='SmartRetail', font=('TkDefaultFont', 21, 'bold'), fg=DARK, bg='#211C12').pack(anchor='w')
        tk.Label(side, text='ANALYTICS  /  ENTERPRISE', font=('TkDefaultFont', 9, 'bold'), fg=ACCENT, bg='#211C12').pack(anchor='w', pady=(3, 25))
        tk.Label(side, text='DATA SOURCE', font=('TkDefaultFont', 9, 'bold'), fg=MUTED, bg='#211C12').pack(anchor='w', pady=(0, 8))
        self._button(side, 'Choose dataset', self.choose_input).pack(fill='x')
        tk.Label(side, textvariable=self.path, wraplength=215, justify='left', fg=DARK, bg='#211C12').pack(anchor='w', pady=10)
        tk.Label(side, text='ANALYSIS VIEW', font=('TkDefaultFont', 9, 'bold'), fg=MUTED, bg='#211C12').pack(anchor='w', pady=(22, 8))
        names = ['Peak sales', 'Customer segments', 'Seasonal & promo', 'Product revenue', 'Anomaly alerts', 'Store & region']
        self.analysis_labels = dict(zip(names, ANALYSES))
        self.analysis_menu = ttk.Combobox(side, values=names, state='readonly')
        self.analysis_menu.current(0); self.analysis_menu.pack(fill='x')
        self.analysis_menu.bind('<<ComboboxSelected>>', self._analysis_changed)
        self._button(side, '▶   Run analysis', self.run, primary=True).pack(fill='x', pady=(18, 7))
        self._button(side, 'View quarantine log', lambda: DLQWindow(self.root, self.facade.get_dlq())).pack(fill='x', pady=3)
        self._button(side, 'Export report', self.export).pack(fill='x', pady=3)
        self.loader_slot=tk.Frame(side,bg='#211C12',height=50);self.loader_slot.pack(fill='x');self.loader_slot.pack_propagate(False)
        self.loader_group=tk.Frame(self.loader_slot,bg='#211C12')
        self.loader = tk.Canvas(self.loader_group,width=40,height=40,bg='#211C12',highlightthickness=0)
        self.loader.pack(side='left')
        self._loader_track=self.loader.create_oval(5,5,35,35,outline='#493E2B',width=3)
        self._loader_arc=self.loader.create_arc(4,4,36,36,start=20,extent=105,style='arc',outline=ACCENT,width=4)
        self._loader_arc2=self.loader.create_arc(4,4,36,36,start=175,extent=35,style='arc',outline=GOLD,width=3)
        self.loader.create_oval(17,17,23,23,fill=ACCENT,outline='')
        self.loader.tag_raise(self._loader_arc)
        self.loader.tag_raise(self._loader_arc2)
        self.loader_text=tk.Label(self.loader_group,text='Processing…',fg=MUTED,bg='#211C12',font=('TkDefaultFont',9,'bold'),anchor='w')
        self.loader_text.pack(side='left',padx=(8,0))
        self.loader_group.place_forget()
        self._loader_angle=20;self._loader_running=False
        tk.Frame(side, bg='#211C12').pack(fill='both', expand=True)
        tk.Label(side, text='Streaming analysis  •  Decimal-safe', fg=MUTED, bg='#211C12', font=('TkDefaultFont', 9)).pack(anchor='w')

        main = tk.Frame(self.root, bg=BG, padx=26, pady=22); main.pack(side='left', fill='both', expand=True)
        header = tk.Frame(main, bg=BG); header.pack(fill='x')
        tk.Label(header, text='Retail performance', font=('TkDefaultFont', 23, 'bold'), fg=DARK, bg=BG).pack(side='left')
        tk.Label(header, textvariable=self.status, font=('TkDefaultFont', 10), fg=MUTED, bg=BG).pack(side='right')
        self.cards = tk.Frame(main, bg=BG); self.cards.pack(fill='x', pady=(0, 16))
        self.kpis = {}
        for key, title, initial in [('rows','ROWS PROCESSED','—'),('revenue','NET REVENUE','—'),('dlq','QUARANTINED','—'),('speed','ELAPSED TIME','—')]:
            shell=RoundedSurface(self.cards,color=PANEL,radius=14,inset=14);shell.configure(height=100);shell.pack_propagate(False);shell.pack(side='left',fill='x',expand=True,padx=(0,10));card=shell.content
            tk.Label(card,text=title,fg=MUTED,bg=PANEL,font=('TkDefaultFont',9,'bold')).pack(anchor='w')
            label=tk.Label(card,text=initial,fg=DARK,bg=PANEL,font=('TkDefaultFont',18,'bold'));label.pack(anchor='w',pady=(7,0));self.kpis[key]=label

        chart_shell=RoundedSurface(main,color=PANEL,radius=19,inset=17);chart_shell.pack(fill='both',expand=True);self.chart_panel=chart_shell.content
        self.chart_title = tk.Label(self.chart_panel, text='Analysis overview', fg=DARK, bg=PANEL, font=('TkDefaultFont', 14, 'bold'))
        self.chart_title.pack(anchor='w', padx=18, pady=(14, 0))
        self.chart_host = tk.Frame(self.chart_panel, bg=PANEL); self.chart_host.pack(fill='both', expand=True, padx=12, pady=8)
        self._placeholder()

    def _button(self, parent, text, command, primary=False):
        return MaterialButton(parent,text,command,ACCENT if primary else SLATE,foreground=BG if primary else DARK)

    def _analysis_changed(self, _event=None):
        label=self.analysis_menu.get(); self.analysis.set(self.analysis_labels[label])

    def _placeholder(self):
        tk.Label(self.chart_host, text='Choose an analysis and run it to see its chart and data breakdown.',
                 fg=DARK, bg=PANEL, font=('TkDefaultFont', 12)).pack(expand=True)

    def choose_input(self):
        path=filedialog.askopenfilename(filetypes=[('Data files','*.csv *.log'),('All files','*')])
        if path:self.path.set(path)
    def chooseInput(self,path,format=None):self.path.set(path)
    def chooseAnalysis(self,kind):self.analysis.set(kind)

    def run(self):
        if not self.path.get():messagebox.showinfo('Dataset required','Choose a CSV or log file first.');return
        self._analysis_changed(); self._start_loader(); self.status.set('Processing dataset…')
        self._button_state('disabled')
        def worker():
            try:
                result=self.facade.run_analysis(self.path.get(),Path(self.path.get()).suffix.lstrip('.'),self.analysis.get())
                self.last_result=result; self.root.after(0,lambda:self.showResults(result))
            except Exception as exc:self.root.after(0,lambda:messagebox.showerror('Analysis failed',str(exc)))
            finally:self.root.after(0,self._finish_run)
        Thread(target=worker,daemon=True).start()

    def _button_state(self,state):
        # Keep the sidebar responsive while a worker processes the file.
        pass
    def _start_loader(self):
        if self._loader_running:return
        self._loader_running=True
        self.loader_group.place(relx=.5,rely=.5,anchor='center')
        self._spin_loader()
    def _spin_loader(self):
        if not self._loader_running:return
        self._loader_angle=(self._loader_angle+18)%360
        self.loader.itemconfigure(self._loader_arc,start=self._loader_angle)
        self.loader.itemconfigure(self._loader_arc2,start=(self._loader_angle+155)%360)
        self.root.after(35,self._spin_loader)
    def _finish_run(self):
        self._loader_running=False;self.loader_group.place_forget();self._button_state('normal')
    def showProgress(self,percent):self.status.set(f'Processing {percent:.0f}%')

    def showResults(self,result):
        total=result.summary.get('total_rows',0); dlq=self.facade.get_dlq().count(); elapsed=result.execution_time_sec
        revenue=result.summary.get('net_revenue','—')
        try:revenue=f'LKR {Decimal(str(revenue)):,.2f}'
        except Exception:pass
        self.kpis['rows'].configure(text=f'{total:,}')
        self.kpis['revenue'].configure(text=revenue)
        self.kpis['dlq'].configure(text=f'{dlq:,}')
        self.kpis['speed'].configure(text=f'{elapsed:.2f}s')
        self.status.set(f'{result.strategy_name.replace("Strategy", "")}  •  complete')
        self.chart_title.configure(text=self._chart_title())
        self._draw_dashboard(result)

    def _chart_title(self):
        return {'peak_sales':'Transaction activity by hour and weekday','customer_segmentation':'Customer segments','seasonal_demand':'Monthly net revenue','product_revenue':'Revenue by product category','anomaly_detection':'Detected alerts','store_regional_performance':'Store revenue ranking'}.get(self.analysis.get(),'Analysis overview')

    def _draw_dashboard(self,result):
        for child in self.chart_host.winfo_children():child.destroy()
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            tk.Label(self.chart_host,text='Install matplotlib to display charts.',fg=DARK,bg=PANEL).pack(pady=30);return
        fig=Figure(figsize=(8,4.5),dpi=100,facecolor=PANEL)
        ax=fig.add_subplot(111);ax.set_facecolor(PANEL);ax.tick_params(colors=DARK);ax.xaxis.label.set_color(DARK);ax.yaxis.label.set_color(DARK)
        for spine in ax.spines.values():spine.set_color(SLATE)
        tables=result.tables; kind=self.analysis.get()
        if kind=='peak_sales':
            matrix=result.charts_data.get('heatmap',[[0]*7 for _ in range(24)])
            ax.remove();left,right=fig.subplots(1,2)
            for chart in (left,right):
                chart.set_facecolor(PANEL);chart.tick_params(colors=DARK)
                for spine in chart.spines.values():spine.set_color(SLATE)
            hours=[sum(matrix[h]) for h in range(24)]
            left.bar(range(24),hours,color=TEAL,width=.78);left.set_title('Transactions by hour',color=DARK,pad=12);left.set_xlabel('Hour of day');left.set_ylabel('Transactions');left.set_xticks(range(0,24,2))
            weekdays=[sum(matrix[h][d] for h in range(24)) for d in range(7)]
            right.bar(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],weekdays,color=GOLD,width=.68);right.set_title('Transactions by weekday',color=DARK,pad=12);right.set_ylabel('Transactions');right.tick_params(axis='x',labelrotation=25)
        elif kind=='customer_segmentation':
            rows=tables.get('segments',[]);ax.pie([r['customers'] for r in rows],labels=[r['segment'] for r in rows],autopct='%1.1f%%',startangle=90,colors=[TEAL,CORAL,GOLD,LAVENDER],textprops={'color':DARK});ax.axis('equal')
        elif kind=='seasonal_demand':
            rows=tables.get('monthly_revenue',[]);xs=[r['month'] for r in rows];ys=[float(r['revenue']) for r in rows];ax.plot(xs,ys,marker='o',linewidth=2.5,color=TEAL);ax.fill_between(xs,ys,alpha=.15,color=TEAL);ax.set_xticks(range(1,13));ax.set_xlabel('Month');ax.set_ylabel('Net revenue')
        elif kind=='product_revenue':
            rows=tables.get('categories',[])[:12];rows=list(reversed(rows));ax.barh([r['name'] for r in rows],[float(r['revenue']) for r in rows],color=TEAL);ax.set_xlabel('Net revenue')
        elif kind=='store_regional_performance':
            rows=tables.get('stores',[])[:15];rows=list(reversed(rows));ax.barh([r['store_id'] for r in rows],[float(r['revenue']) for r in rows],color=GOLD);ax.set_xlabel('Net revenue')
        else:
            rows=tables.get('alert_breakdown',[])
            if rows:
                palette=[CORAL,GOLD,LAVENDER];rows=list(reversed(rows));ax.barh([r['alert_type'] for r in rows],[r['count'] for r in rows],color=[palette[i%len(palette)] for i in range(len(rows))])
            else:ax.text(.5,.5,'No anomalies detected',ha='center',va='center',color=DARK,transform=ax.transAxes,fontsize=14)
            ax.set_xlabel('Number of alerts');ax.set_title(f"{result.summary.get('alert_count',0):,} flagged events",color=DARK);ax.grid(axis='x',color=SLATE,alpha=.5);ax.set_axisbelow(True)
        fig.tight_layout(pad=2)
        canvas=FigureCanvasTkAgg(fig,master=self.chart_host);canvas.draw();canvas.get_tk_widget().pack(fill='both',expand=True)
        # Show a readable breakdown below the chart, capped to keep the dashboard fast.
        rows=next((v for v in tables.values() if v),[])
        if rows:
            holder=tk.Frame(self.chart_host,bg=PANEL);holder.pack(fill='x',padx=5,pady=(0,8))
            cols=list(rows[0].keys());tree=ttk.Treeview(holder,columns=cols,show='headings',height=min(5,len(rows)))
            for col in cols:tree.heading(col,text=col.replace('_',' ').title());tree.column(col,width=140,anchor='w')
            for row in rows[:8]:tree.insert('','end',values=[row.get(c,'') for c in cols])
            tree.pack(fill='x')

    def show_results(self,result):self.showResults(result)
    def export(self):
        if not hasattr(self,'last_result'):messagebox.showinfo('No results','Run an analysis before exporting.');return
        path=filedialog.asksaveasfilename(defaultextension='.pdf',filetypes=[('PDF summary report','*.pdf'),('CSV data export','*.csv'),('HTML report','*.html')])
        if path:
            fmt='html' if path.lower().endswith('.html') else 'csv' if path.lower().endswith('.csv') else 'pdf'
            try:self.facade.export_result(self.last_result,fmt,path)
            except Exception as exc:messagebox.showerror('Export failed',str(exc))
    def start(self):self.root.mainloop()
