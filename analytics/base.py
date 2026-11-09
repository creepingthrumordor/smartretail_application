"""Interface for incremental analytics strategies."""

from abc import ABC, abstractmethod
from decimal import Decimal

from smartretail.core.domain import AnalyticsResult, TransactionRecord


class IAnalyticsStrategy(ABC):
    """Accumulate chunk data and build a result at end of stream."""

    def __init__(self) -> None:
        self.records = 0
        self.revenue = Decimal("0")

    def consume(self, records: list[TransactionRecord]) -> None:
        self.records += len(records)
        self.revenue += sum(
            (record.total_amount for record in records), start=Decimal("0")
        )

    @abstractmethod
    def build_result(self) -> AnalyticsResult:
        """Return the accumulated analysis result."""
        raise NotImplementedError
