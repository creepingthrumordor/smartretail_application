"""Interface for transformations applied to transaction batches."""

from abc import ABC, abstractmethod

from smartretail.core.domain import TransactionRecord


class ITransformation(ABC):
    """Transform a batch and return the next batch in the pipeline."""

    @abstractmethod
    def apply(self, records: list[TransactionRecord]) -> list[TransactionRecord]:
        raise NotImplementedError
