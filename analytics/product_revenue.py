"""Revenue rollups across regions, stores, categories, and products."""

from collections import Counter, defaultdict

from smartretail.core.domain import AnalyticsResult, TransactionRecord
from .base import IAnalyticsStrategy


class ProductRevenueStrategy(IAnalyticsStrategy):
    """Aggregate revenue and return/sale units across product dimensions."""

    def __init__(self) -> None:
        super().__init__()
        self.categories: Counter[str] = Counter()
        self.products: Counter[str] = Counter()
        self.regions: Counter[str] = Counter()
        self.stores: Counter[str] = Counter()
        self.quantity_by_category: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    def consume(self, records: list[TransactionRecord]) -> None:
        super().consume(records)
        for record in records:
            amount = record.total_amount
            self.categories[record.product_category] += amount
            self.products[record.product_name] += amount
            self.regions[record.region] += amount
            self.stores[record.store_id] += amount
            return_index = 0 if record.is_return else 1
            self.quantity_by_category[record.product_category][return_index] += abs(
                record.quantity
            )

    @staticmethod
    def _ranking(counter: Counter[str]) -> list[dict[str, str]]:
        return [
            {"name": name, "revenue": str(amount)}
            for name, amount in counter.most_common(20)
        ]

    def build_result(self) -> AnalyticsResult:
        return AnalyticsResult(
            strategy_name=type(self).__name__,
            summary={"records": self.records, "net_revenue": str(self.revenue)},
            tables={
                "categories": self._ranking(self.categories),
                "products": self._ranking(self.products),
                "regions": self._ranking(self.regions),
                "stores": self._ranking(self.stores),
            },
        )
