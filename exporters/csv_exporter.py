import csv,json,os
from smartretail.core.exceptions import ExportError
class CsvExporter:
 def export(self,result,destination):
  try:
   with open(destination,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['section','key','value']);w.writerows(('summary',k,json.dumps(v,default=str)) for k,v in result.summary.items())
    for name,rows in result.tables.items():
     w.writerow([name]);
     if rows:
      writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
   return destination
  except OSError as exc:raise ExportError(f'Could not write CSV export: {exc}') from exc
