"""Incremental customer frequency and spend segmentation."""

from collections import defaultdict
from decimal import Decimal

from smartretail.core.domain import AnalyticsResult, TransactionRecord
from .base import IAnalyticsStrategy


class CustomerSegmentationStrategy(IAnalyticsStrategy):
    """Group identified customers by order frequency and spending."""

    def __init__(self) -> None:
        super().__init__()
        self.customers: dict[str, list[int | Decimal]] = defaultdict(
            lambda: [0, Decimal("0")]
        )

    def consume(self, records: list[TransactionRecord]) -> None:
        super().consume(records)
        for record in records:
            if record.customer_id:
                profile = self.customers[record.customer_id]
                profile[0] += 1
                profile[1] += record.total_amount

    def build_result(self) -> AnalyticsResult:
        unknown_rows = self.records - sum(
            int(profile[0]) for profile in self.customers.values()
        )
        tiers = {
            "Frequent Customers": 0,
            "Occasional Customers": 0,
            "One-Time Customers": 0,
            "Unknown Customers": unknown_rows,
        }
        for order_count, spend in self.customers.values():
            if order_count >= 10 or spend >= 500:
                segment = "Frequent Customers"
            elif order_count > 1:
                segment = "Occasional Customers"
            else:
                segment = "One-Time Customers"
            tiers[segment] += 1

        rows = [
            {"segment": segment, "customers": count}
            for segment, count in tiers.items()
        ]
        return AnalyticsResult(
            strategy_name=type(self).__name__,
            summary={"records": self.records, "segments": tiers},
            tables={"segments": rows},
        )
