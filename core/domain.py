"""Typed domain objects shared by the application layers."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional


@dataclass(frozen=True)
class RawRecord:
    """A source row before it has been validated."""

    source: str
    line_number: int
    data: str


@dataclass(frozen=True)
class TransactionRecord:
    """A validated retail transaction."""

    transaction_id: str
    transaction_datetime: datetime
    store_id: str
    store_city: str
    region: str
    warehouse_id: str
    customer_id: Optional[str]
    customer_age: Optional[int]
    customer_gender: Optional[str]
    customer_city: Optional[str]
    product_category: str
    product_name: str
    quantity: int
    unit_price: Decimal
    discount_percent: Optional[Decimal]
    promotion_name: Optional[str]
    payment_method: str
    channel: str
    total_amount: Decimal
    stock_on_hand: int
    reorder_level: int
    transaction_type: str
    is_return: bool = False


@dataclass(frozen=True)
class DLQRecord:
    """A rejected source row and its validation diagnostic."""

    source: str
    line_number: int
    raw_data: str
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AnalyticsResult:
    """Summary, tabular data, charts, and alerts for one analysis."""

    strategy_name: str
    summary: dict[str, Any] = field(default_factory=dict)
    tables: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    charts_data: dict[str, Any] = field(default_factory=dict)
    alerts: list[str] = field(default_factory=list)
    execution_time_sec: float = 0.0
