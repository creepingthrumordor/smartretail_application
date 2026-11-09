"""Hourly and weekday sales activity analytics."""

from collections import Counter

from smartretail.core.domain import AnalyticsResult, TransactionRecord
from .base import IAnalyticsStrategy


class PeakSalesStrategy(IAnalyticsStrategy):
    """Count activity for each hour/day pair and store."""

    def __init__(self) -> None:
        super().__init__()
        self.hours: Counter[tuple[int, int]] = Counter()
        self.stores: Counter[str] = Counter()

    def consume(self, records: list[TransactionRecord]) -> None:
        super().consume(records)
        for record in records:
            key = (record.transaction_datetime.hour, record.transaction_datetime.weekday())
            self.hours[key] += 1
            self.stores[record.store_id] += 1

    def build_result(self) -> AnalyticsResult:
        peak_hours = [
            {"hour": hour, "weekday": weekday, "count": count}
            for (hour, weekday), count in self.hours.most_common()
        ]
        store_workload = [
            {"store_id": store_id, "transactions": count}
            for store_id, count in self.stores.most_common()
        ]
        heatmap = [
            [self.hours[(hour, weekday)] for weekday in range(7)]
            for hour in range(24)
        ]
        return AnalyticsResult(
            strategy_name=type(self).__name__,
            summary={"records": self.records, "net_revenue": str(self.revenue)},
            tables={"peak_hours": peak_hours, "stores": store_workload},
            charts_data={"heatmap": heatmap},
        )
