"""Public facade coordinating input, processing, analytics, and export."""

import os
import time
from collections.abc import Callable

from smartretail.adapters.base import IInputAdapter
from smartretail.adapters.csv_adapter import CsvInputAdapter
from smartretail.adapters.log_adapter import LogInputAdapter
from smartretail.analytics.base import IAnalyticsStrategy
from smartretail.analytics.anomaly_detection import AnomalyDetectionStrategy
from smartretail.analytics.customer_segmentation import CustomerSegmentationStrategy
from smartretail.analytics.peak_sales import PeakSalesStrategy
from smartretail.analytics.product_revenue import ProductRevenueStrategy
from smartretail.analytics.seasonal_demand import SeasonalDemandStrategy
from smartretail.analytics.store_regional import StoreRegionalPerformanceStrategy
from smartretail.config import ANALYSES
from smartretail.core.domain import AnalyticsResult
from smartretail.core.exceptions import InputFormatError
from smartretail.exporters.base import IResultExporter
from smartretail.exporters.csv_exporter import CsvExporter
from smartretail.exporters.visual_exporter import VisualReportExporter
from smartretail.pipeline.builder import PipelineBuilder
from smartretail.validation.dead_letter_queue import DeadLetterQueue
from .chunk_service import ChunkProcessingService, ProgressCallback

AdapterFactory = Callable[[], IInputAdapter]
StrategyFactory = Callable[[], IAnalyticsStrategy]
ExporterFactory = Callable[[], IResultExporter]

DEFAULT_ADAPTERS: dict[str, AdapterFactory] = {
    "csv": CsvInputAdapter,
    "log": LogInputAdapter,
}
DEFAULT_STRATEGIES: dict[str, StrategyFactory] = dict(
    zip(
        ANALYSES,
        (
            PeakSalesStrategy,
            CustomerSegmentationStrategy,
            SeasonalDemandStrategy,
            ProductRevenueStrategy,
            AnomalyDetectionStrategy,
            StoreRegionalPerformanceStrategy,
        ),
    )
)
DEFAULT_EXPORTERS: dict[str, ExporterFactory] = {
    "csv": CsvExporter,
    "pdf": VisualReportExporter,
    "html": VisualReportExporter,
}


class SmartRetailFacade:
    """Provide a small, replaceable application interface to the GUI."""

    def __init__(
        self,
        dlq: DeadLetterQueue | None = None,
        adapter_factories: dict[str, AdapterFactory] | None = None,
        strategy_factories: dict[str, StrategyFactory] | None = None,
        exporter_factories: dict[str, ExporterFactory] | None = None,
    ) -> None:
        self.dlq = dlq or DeadLetterQueue()
        self.adapter_factories = adapter_factories or DEFAULT_ADAPTERS
        self.strategy_factories = strategy_factories or DEFAULT_STRATEGIES
        self.exporter_factories = exporter_factories or DEFAULT_EXPORTERS

    def run_analysis(
        self,
        file_path: str,
        format_type: str = "csv",
        analysis_type: str = "peak_sales",
        chunk_size: int = 5000,
        progress_callback: ProgressCallback | None = None,
    ) -> AnalyticsResult:
        if not os.path.isfile(file_path):
            raise InputFormatError(f"Input file does not exist: {file_path}")

        adapter_factory = self.adapter_factories.get(format_type.lower())
        if adapter_factory is None:
            raise InputFormatError(f"Unsupported input format: {format_type}")

        strategy_factory = self.strategy_factories.get(analysis_type)
        if strategy_factory is None:
            raise InputFormatError(f"Unknown analysis: {analysis_type}")

        adapter = adapter_factory()
        strategy = strategy_factory()
        pipeline = PipelineBuilder().build()
        service = ChunkProcessingService(strategy, self.dlq, pipeline)
        started_at = time.perf_counter()
        result = service.run(adapter, file_path, chunk_size, progress_callback)
        result.execution_time_sec = time.perf_counter() - started_at
        return result

    def runAnalysis(
        self,
        path: str,
        format: str,
        analysis: str,
        chunkSize: int = 5000,
        progress_callback: ProgressCallback | None = None,
    ) -> AnalyticsResult:
        return self.run_analysis(
            path, format, analysis, chunkSize, progress_callback
        )

    def export_result(
        self,
        result: AnalyticsResult,
        format_type: str,
        destination: str,
    ) -> str | None:
        exporter_factory = self.exporter_factories.get(format_type.lower())
        if exporter_factory is None:
            raise InputFormatError(f"Unsupported export format: {format_type}")
        return exporter_factory().export(result, destination)

    def export(
        self, result: AnalyticsResult, format: str, destination: str
    ) -> str | None:
        return self.export_result(result, format, destination)

    def get_dlq(self) -> DeadLetterQueue:
        return self.dlq
