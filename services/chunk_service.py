"""Coordinate validation, deduplication, transformations, and analytics."""

from datetime import datetime
from typing import Callable

from smartretail.adapters.base import IInputAdapter
from smartretail.analytics.base import IAnalyticsStrategy
from smartretail.core.domain import (
    AnalyticsResult,
    DLQRecord,
    RawRecord,
    TransactionRecord,
)
from smartretail.pipeline.pipeline import ProcessingPipeline
from smartretail.validation.dead_letter_queue import DeadLetterQueue
from smartretail.validation.duplicate_detector import DuplicateDetector
from smartretail.validation.validator import RecordValidator


ProgressCallback = Callable[[float, int, int], None]


class ChunkProcessingService:
    """Process bounded input chunks and feed valid records to a strategy."""

    def __init__(
        self,
        strategy: IAnalyticsStrategy,
        dlq: DeadLetterQueue,
        pipeline: ProcessingPipeline | None = None,
        validator: RecordValidator | None = None,
        duplicate_detector: DuplicateDetector | None = None,
    ) -> None:
        self.strategy = strategy
        self.dlq = dlq
        self.pipeline = pipeline
        self.validator = validator or RecordValidator()
        self.duplicates = duplicate_detector or DuplicateDetector()
        self.processed = 0

    def process_stream(
        self,
        adapter: IInputAdapter,
        chunk_size: int,
        progress_callback: ProgressCallback | None = None,
    ) -> AnalyticsResult:
        while True:
            raw_chunk = adapter.read_chunk(chunk_size)
            if not raw_chunk:
                break

            valid_records = self._validate_chunk(raw_chunk)
            if self.pipeline is not None:
                valid_records = self.pipeline.process_chunk(valid_records)
            self.strategy.consume(valid_records)

            if progress_callback is not None:
                progress_callback(0.0, self.processed, self.dlq.count())

        result = self.strategy.build_result()
        result.summary.update(
            {
                "total_rows": self.processed,
                "duplicates": self.duplicates.duplicates,
                "quarantined": self.dlq.count(),
            }
        )
        return result

    def _validate_chunk(
        self, raw_chunk: list[RawRecord]
    ) -> list[TransactionRecord]:
        valid_records: list[TransactionRecord] = []
        for raw in raw_chunk:
            self.processed += 1
            record, error = self.validator.parse_and_validate(raw)
            if error is not None:
                self._quarantine(raw.source, raw.line_number, raw.data, error)
                continue
            assert record is not None

            state = self.duplicates.check(record)
            if state == "duplicate":
                continue
            if state == "conflict":
                self._quarantine(
                    raw.source,
                    raw.line_number,
                    raw.data,
                    "Conflicting duplicate transaction_id",
                )
                continue
            valid_records.append(record)
        return valid_records

    def _quarantine(self, source: str, line_number: int, data: str, reason: str) -> None:
        self.dlq.add(
            DLQRecord(
                source=source,
                line_number=line_number,
                raw_data=data,
                reason=reason,
                timestamp=datetime.now(),
            )
        )

    def run(
        self,
        adapter: IInputAdapter,
        path: str,
        chunk_size: int,
        progress_callback: ProgressCallback | None = None,
    ) -> AnalyticsResult:
        adapter.open(path)
        try:
            return self.process_stream(adapter, chunk_size, progress_callback)
        finally:
            adapter.close()
