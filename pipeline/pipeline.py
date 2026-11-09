"""Ordered execution of a configurable transformation chain."""

from smartretail.core.domain import TransactionRecord
from .base import ITransformation


class ProcessingPipeline:
    """Apply each configured transformation to an input batch in order."""

    def __init__(self, steps: tuple[ITransformation, ...] | list[ITransformation] = ()) -> None:
        self.steps = tuple(steps)

    def process_chunk(self, records: list[TransactionRecord]) -> list[TransactionRecord]:
        for transformation in self.steps:
            records = transformation.apply(records)
        return records
