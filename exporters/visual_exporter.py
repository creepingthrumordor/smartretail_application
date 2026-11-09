"""Export printable PDF or HTML analysis reports."""
import html
import json
from datetime import datetime

from smartretail.core.exceptions import ExportError

class VisualReportExporter:
    def export(self, result, destination):
        try:
            if destination.lower().endswith('.pdf'):
                return self._export_pdf(result, destination)
            target=destination if destination.lower().endswith('.html') else destination+'.html'
            body=(f'<h1>{html.escape(result.strategy_name)}</h1><h2>Summary</h2>'
                  f'<pre>{html.escape(json.dumps(result.summary,indent=2,default=str))}</pre>'
                  f'<h2>Tables</h2><pre>{html.escape(json.dumps(result.tables,indent=2,default=str))}</pre>'
                  f'<h2>Alerts</h2><pre>{html.escape("\n".join(result.alerts))}</pre>')
            with open(target,'w',encoding='utf-8') as file:
                file.write('<!doctype html><meta charset="utf-8"><title>SmartRetail Report</title>'
                           '<body style="font:16px sans-serif;max-width:1000px;margin:3rem auto">'+body+'</body>')
            return target
        except (OSError, ImportError, ValueError) as exc:
            raise ExportError(f'Could not create analysis report: {exc}') from exc

    def _export_pdf(self,result,destination):
        from matplotlib.backends.backend_pdf import PdfPages
        from matplotlib.figure import Figure
        from matplotlib.patches import FancyBboxPatch

        summary=result.summary; tables=result.tables; name=result.strategy_name.lower()
        paper='#FBFAF8'; ink='#302C27'; muted='#77716A'; accent='#F99F46'; teal='#4ABDAC'; gold='#F7B733'
        fig=Figure(figsize=(8.27,11.69),facecolor=paper)
        header=fig.add_axes([0,0,1,1]);header.axis('off')
        header.text(.075,.945,'SMARTRETAIL  /  ANALYTICS',fontsize=9,weight='bold',color=muted)
        header.text(.075,.902,result.strategy_name.replace('Strategy',' Analysis'),fontsize=23,weight='bold',color=ink)
        header.text(.075,.875,f"Summary report  ·  {datetime.now():%d %b %Y}",fontsize=10,color=muted)
        header.add_patch(FancyBboxPatch((.075,.851),.85,.004,boxstyle='round,pad=0.002',facecolor=accent,edgecolor='none'))

        row_count=summary.get('total_rows',summary.get('records','—'))
        try:row_count=f'{int(row_count):,}'
        except (TypeError,ValueError):pass
        revenue=summary.get('net_revenue','—')
        try:revenue=f'LKR {float(revenue):,.2f}'
        except (TypeError,ValueError):pass
        quarantined=summary.get('quarantined','—')
        try:quarantined=f'{int(quarantined):,}'
        except (TypeError,ValueError):pass
        metrics=[('Rows processed',row_count),
                 ('Net revenue',revenue),
                 ('Quarantined',quarantined),
                 ('Elapsed',f'{result.execution_time_sec:.1f} sec')]
        for i,(label,value) in enumerate(metrics):
            x=.075+i*.218
            header.add_patch(FancyBboxPatch((x,.756),.198,.072,boxstyle='round,pad=0.009,rounding_size=0.012',facecolor='#F0EDE8',edgecolor='none'))
            header.text(x+.012,.801,label.upper(),fontsize=7.5,weight='bold',color=muted)
            header.text(x+.012,.774,str(value),fontsize=12.5,weight='bold',color=ink)

        header.text(.075,.718,'At a glance',fontsize=13,weight='bold',color=ink)
        chart=fig.add_axes([.11,.405,.80,.285]);chart.set_facecolor(paper)
        for spine in chart.spines.values():spine.set_visible(False)
        chart.tick_params(colors=muted,labelsize=8);chart.grid(axis='y',color='#E8E3DC',linewidth=.7);chart.set_axisbelow(True)
        if 'peak' in name and result.charts_data.get('heatmap'):
            matrix=result.charts_data['heatmap']; values=[sum(matrix[h]) for h in range(24)]
            chart.bar(range(24),values,color=teal,width=.75);chart.set_xticks(range(0,24,2));chart.set_xlabel('Hour of day',color=muted);chart.set_ylabel('Transactions',color=muted)
        elif 'customer' in name and tables.get('segments'):
            rows=tables['segments'];chart.pie([r['customers'] for r in rows],labels=[r['segment'].replace(' Customers','') for r in rows],autopct='%1.0f%%',startangle=90,colors=[teal,accent,gold,'#AAA6A0'],textprops={'color':ink,'fontsize':8},wedgeprops={'width':.38,'edgecolor':paper})
        elif 'seasonal' in name and tables.get('monthly_revenue'):
            rows=tables['monthly_revenue'];chart.plot([r['month'] for r in rows],[float(r['revenue']) for r in rows],color=teal,marker='o',markersize=4,linewidth=2);chart.set_xticks(range(1,13));chart.set_xlabel('Month',color=muted);chart.set_ylabel('Net revenue',color=muted)
        elif 'product' in name and tables.get('categories'):
            rows=list(reversed(tables['categories'][:8]));chart.barh([r['name'] for r in rows],[float(r['revenue']) for r in rows],color=teal);chart.set_xlabel('Net revenue',color=muted)
        elif 'anomaly' in name and tables.get('alert_breakdown'):
            rows=list(reversed(tables['alert_breakdown']));chart.barh([r['alert_type'] for r in rows],[r['count'] for r in rows],color=accent);chart.set_xlabel('Alert count',color=muted)
        elif 'store' in name and tables.get('stores'):
            rows=list(reversed(tables['stores'][:8]));chart.barh([r['store_id'] for r in rows],[float(r['revenue']) for r in rows],color=gold);chart.set_xlabel('Net revenue',color=muted)
        else:
            chart.axis('off');chart.text(.5,.5,'No chart data available',ha='center',va='center',color=muted)

        header.text(.075,.365,'Key results',fontsize=13,weight='bold',color=ink)
        primary_names={'peak':'peak_hours','customer':'segments','seasonal':'monthly_revenue','product':'categories','anomaly':'alert_breakdown','store':'stores'}
        table_key=next((v for k,v in primary_names.items() if k in name and tables.get(v)),None)
        rows=(tables.get(table_key,[])[:6] if table_key else [])
        if rows:
            table_ax=fig.add_axes([.075,.125,.85,.215]);table_ax.axis('off')
            columns=list(rows[0].keys())[:4]
            cells=[[str(row.get(col,''))[:42] for col in columns] for row in rows]
            table=table_ax.table(cellText=cells,colLabels=[c.replace('_',' ').title() for c in columns],cellLoc='left',colLoc='left',bbox=[0,0,1,1])
            table.auto_set_font_size(False);table.set_fontsize(8)
            for (row,col),cell in table.get_celld().items():
                cell.set_linewidth(0)
                if row==0:cell.set_facecolor('#E9E4DC');cell.set_text_props(weight='bold',color=ink)
                else:cell.set_facecolor('#FFFFFF' if row%2 else '#F4F1EC');cell.set_text_props(color=ink)
        else:
            header.text(.08,.30,'No tabular results were returned for this analysis.',fontsize=10,color=muted)
        header.text(.075,.065,'SmartRetail Analytics',fontsize=8,color=muted)
        header.text(.925,.065,'CONFIDENTIAL',fontsize=8,color=muted,ha='right')
        with PdfPages(destination) as pdf:pdf.savefig(fig)
        fig.clear()
        return destination
