"""Fluent builder for processing pipelines."""

from collections.abc import Callable

from smartretail.core.domain import TransactionRecord
from .pipeline import ProcessingPipeline
from .transformations import (
    AggregationTransformation,
    EnrichmentTransformation,
    FilterTransformation,
)
from .base import ITransformation


class PipelineBuilder:
    """Assemble a pipeline without coupling callers to its internals."""

    def __init__(self) -> None:
        self._steps: list[ITransformation] = []

    def add_filter(
        self, predicate: Callable[[TransactionRecord], bool]
    ) -> "PipelineBuilder":
        self._steps.append(FilterTransformation(predicate))
        return self

    def add_enrichment(
        self, enricher: Callable[[TransactionRecord], TransactionRecord]
    ) -> "PipelineBuilder":
        self._steps.append(EnrichmentTransformation(enricher))
        return self

    def add_aggregation(
        self,
        aggregator: Callable[[list[TransactionRecord]], list[TransactionRecord]],
    ) -> "PipelineBuilder":
        self._steps.append(AggregationTransformation(aggregator))
        return self

    def build(self) -> ProcessingPipeline:
        return ProcessingPipeline(self._steps)
