import html,json,os
from smartretail.core.exceptions import ExportError
class VisualReportExporter:
 def export(self,result,destination):
  try:
   target=destination if destination.lower().endswith('.html') else destination+'.html'
   body=f'<h1>{html.escape(result.strategy_name)}</h1><h2>Summary</h2><pre>{html.escape(json.dumps(result.summary,indent=2,default=str))}</pre><h2>Tables</h2><pre>{html.escape(json.dumps(result.tables,indent=2,default=str))}</pre><h2>Alerts</h2><pre>{html.escape("\n".join(result.alerts))}</pre>'
   with open(target,'w',encoding='utf-8') as f:f.write('<!doctype html><meta charset="utf-8"><title>SmartRetail Report</title><body style="font:16px sans-serif;max-width:1000px;margin:3rem auto">'+body+'</body>')
   return target
  except OSError as exc:raise ExportError(f'Could not write report: {exc}') from exc
