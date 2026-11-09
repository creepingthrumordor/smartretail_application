"""Store and region revenue, volume, and inventory comparisons."""

from collections import defaultdict
from decimal import Decimal

from smartretail.core.domain import AnalyticsResult, TransactionRecord
from .base import IAnalyticsStrategy


class StoreRegionalPerformanceStrategy(IAnalyticsStrategy):
    """Accumulate store and regional performance metrics incrementally."""

    def __init__(self) -> None:
        super().__init__()
        self.stores: dict[str, list[Decimal | int]] = defaultdict(
            lambda: [Decimal("0"), 0, 0, 0]
        )
        self.regions: dict[str, list[Decimal | int]] = defaultdict(
            lambda: [Decimal("0"), 0]
        )

    def consume(self, records: list[TransactionRecord]) -> None:
        super().consume(records)
        for record in records:
            store = self.stores[record.store_id]
            store[0] += record.total_amount
            store[1] += 1
            store[2] += record.stock_on_hand
            store[3] += record.reorder_level

            region = self.regions[record.region]
            region[0] += record.total_amount
            region[1] += 1

    def build_result(self) -> AnalyticsResult:
        store_rows = [
            {
                "store_id": store_id,
                "revenue": str(values[0]),
                "transactions": values[1],
                "stock_to_reorder": values[2] / values[3] if values[3] else None,
            }
            for store_id, values in sorted(
                self.stores.items(), key=lambda item: item[1][0], reverse=True
            )
        ]
        region_rows = [
            {
                "region": region_name,
                "revenue": str(values[0]),
                "transactions": values[1],
            }
            for region_name, values in self.regions.items()
        ]
        return AnalyticsResult(
            strategy_name=type(self).__name__,
            summary={"records": self.records, "net_revenue": str(self.revenue)},
            tables={"stores": store_rows, "regions": region_rows},
        )
