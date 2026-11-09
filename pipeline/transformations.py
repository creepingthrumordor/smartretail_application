"""Concrete transformations supported by the processing pipeline."""

from collections.abc import Callable

from smartretail.core.domain import TransactionRecord
from .base import ITransformation


class FilterTransformation(ITransformation):
    """Keep records that satisfy a predicate."""

    def __init__(self, predicate: Callable[[TransactionRecord], bool]) -> None:
        self.predicate = predicate

    def apply(self, records: list[TransactionRecord]) -> list[TransactionRecord]:
        return [record for record in records if self.predicate(record)]


class EnrichmentTransformation(ITransformation):
    """Return transformed versions of each record."""

    def __init__(
        self,
        enricher_func: Callable[[TransactionRecord], TransactionRecord],
    ) -> None:
        self.enricher_func = enricher_func

    def apply(self, records: list[TransactionRecord]) -> list[TransactionRecord]:
        return [self.enricher_func(record) for record in records]


class AggregationTransformation(ITransformation):
    """Apply a batch-level aggregation function."""

    def __init__(
        self,
        agg_func: Callable[[list[TransactionRecord]], list[TransactionRecord]],
    ) -> None:
        self.agg_func = agg_func

    def apply(self, records: list[TransactionRecord]) -> list[TransactionRecord]:
        return self.agg_func(records)
