"""Revenue totals by calendar month and promotion."""

from collections import Counter

from smartretail.core.domain import AnalyticsResult, TransactionRecord
from .base import IAnalyticsStrategy


class SeasonalDemandStrategy(IAnalyticsStrategy):
    """Accumulate monthly and promotional transaction revenue."""

    def __init__(self) -> None:
        super().__init__()
        self.months: Counter[int] = Counter()
        self.promos: Counter[str] = Counter()

    def consume(self, records: list[TransactionRecord]) -> None:
        super().consume(records)
        for record in records:
            self.months[record.transaction_datetime.month] += record.total_amount
            self.promos[record.promotion_name or "None"] += record.total_amount

    def build_result(self) -> AnalyticsResult:
        monthly_revenue = [
            {"month": month, "revenue": str(self.months[month])}
            for month in range(1, 13)
        ]
        promotion_revenue = [
            {"promotion": name, "revenue": str(amount)}
            for name, amount in self.promos.items()
        ]
        return AnalyticsResult(
            strategy_name=type(self).__name__,
            summary={"records": self.records, "net_revenue": str(self.revenue)},
            tables={
                "monthly_revenue": monthly_revenue,
                "promotions": promotion_revenue,
            },
        )
