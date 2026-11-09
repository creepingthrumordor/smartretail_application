import os,time
from smartretail.config import ANALYSES
from smartretail.core.exceptions import InputFormatError
from smartretail.adapters.csv_adapter import CsvInputAdapter
from smartretail.adapters.log_adapter import LogInputAdapter
from smartretail.analytics import peak_sales,customer_segmentation,seasonal_demand,product_revenue,anomaly_detection,store_regional
from smartretail.pipeline.builder import PipelineBuilder
from smartretail.validation.dead_letter_queue import DeadLetterQueue
from .chunk_service import ChunkProcessingService
from smartretail.exporters.csv_exporter import CsvExporter
from smartretail.exporters.visual_exporter import VisualReportExporter
class SmartRetailFacade:
 def __init__(self):self.dlq=DeadLetterQueue()
 def run_analysis(self,file_path,format_type='csv',analysis_type='peak_sales',chunk_size=5000,progress_callback=None):
  if not os.path.isfile(file_path):raise InputFormatError(f'Input file does not exist: {file_path}')
  fmt=format_type.lower(); adapter=CsvInputAdapter() if fmt=='csv' else LogInputAdapter() if fmt=='log' else None
  if adapter is None:raise InputFormatError(f'Unsupported input format: {format_type}')
  strategies={ANALYSES[0]:peak_sales.PeakSalesStrategy,ANALYSES[1]:customer_segmentation.CustomerSegmentationStrategy,ANALYSES[2]:seasonal_demand.SeasonalDemandStrategy,ANALYSES[3]:product_revenue.ProductRevenueStrategy,ANALYSES[4]:anomaly_detection.AnomalyDetectionStrategy,ANALYSES[5]:store_regional.StoreRegionalPerformanceStrategy}
  try:factory=strategies[analysis_type]
  except KeyError:raise InputFormatError(f'Unknown analysis: {analysis_type}')
  start=time.perf_counter();service=ChunkProcessingService(factory(),self.dlq,PipelineBuilder().build());result=service.run(adapter,file_path,chunk_size,progress_callback);result.execution_time_sec=time.perf_counter()-start;return result
 def runAnalysis(self,path,format,analysis,chunkSize=5000,progress_callback=None):return self.run_analysis(path,format,analysis,chunkSize,progress_callback)
 def export_result(self,result,format_type,destination):
  (CsvExporter() if format_type.lower()=='csv' else VisualReportExporter()).export(result,destination)
 def export(self,result,format,destination):return self.export_result(result,format,destination)
 def get_dlq(self):return self.dlq
