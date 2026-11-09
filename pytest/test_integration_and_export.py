from smartretail.config import CSV_FIELDS
from smartretail.services.facade import SmartRetailFacade
from smartretail.core.domain import AnalyticsResult
from smartretail.exporters.visual_exporter import VisualReportExporter

def test_facade_processes_csv_and_deduplicates(write_transactions,transaction_row):
    path=write_transactions([transaction_row,transaction_row.copy()])
    result=SmartRetailFacade().run_analysis(str(path),'csv','peak_sales',chunk_size=1)
    assert result.summary['total_rows']==2
    assert result.summary['duplicates']==1
    assert result.summary['records']==1
    assert result.tables['peak_hours']

def test_pdf_export_creates_one_page_report(tmp_path):
    result=AnalyticsResult('PeakSalesStrategy',{'total_rows':10,'records':10,'net_revenue':'1250.50'},
        {'peak_hours':[{'hour':17,'weekday':1,'count':5}]},
        {'heatmap':[[0]*7 for _ in range(24)]},execution_time_sec=0.25)
    destination=tmp_path/'summary.pdf'
    VisualReportExporter().export(result,str(destination))
    assert destination.exists()
    assert destination.read_bytes().startswith(b'%PDF')
    assert destination.stat().st_size>1000
