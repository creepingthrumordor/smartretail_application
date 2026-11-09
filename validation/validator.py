"""Parse and validate raw rows into transaction domain records."""

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from smartretail.config import CSV_FIELDS
from smartretail.core.domain import RawRecord, TransactionRecord


class RecordValidator:
    """Convert one raw CSV row, returning a record or an error message."""

    def parse_and_validate(
        self, raw: RawRecord
    ) -> tuple[TransactionRecord | None, str | None]:
        try:
            row = next(csv.reader([raw.data]))
            if len(row) != len(CSV_FIELDS):
                return None, f"Expected {len(CSV_FIELDS)} fields, received {len(row)}"

            data = dict(zip(CSV_FIELDS, (value.strip() for value in row)))
            if not data["transaction_id"]:
                return None, "Missing transaction_id"

            timestamp = datetime.strptime(
                data["transaction_datetime"], "%m/%d/%Y %H:%M"
            )
            quantity = int(data["quantity"])
            transaction_type = data["transaction_type"]
            unit_price = Decimal(data["unit_price"])
            total_amount = Decimal(data["total_amount"])

            if transaction_type == "Sale" and unit_price < 0:
                return None, "Negative unit price on Sale"
            if transaction_type == "Return" and quantity >= 0:
                return None, "Return quantity must be negative"

            customer_age = int(data["customer_age"]) if data["customer_age"] else None
            discount = (
                Decimal(data["discount_percent"])
                if data["discount_percent"]
                else None
            )
            record = TransactionRecord(
                transaction_id=data["transaction_id"],
                transaction_datetime=timestamp,
                store_id=data["store_id"],
                store_city=data["store_city"],
                region=data["region"],
                warehouse_id=data["warehouse_id"],
                customer_id=data["customer_id"] or None,
                customer_age=customer_age,
                customer_gender=data["customer_gender"] or None,
                customer_city=data["customer_city"] or None,
                product_category=data["product_category"],
                product_name=data["product_name"],
                quantity=quantity,
                unit_price=unit_price,
                discount_percent=discount,
                promotion_name=data["promotion_name"] or None,
                payment_method=data["payment_method"] or "Unknown",
                channel=data["channel"],
                total_amount=total_amount,
                stock_on_hand=int(data["stock_on_hand"]),
                reorder_level=int(data["reorder_level"]),
                transaction_type=transaction_type,
                is_return=transaction_type == "Return",
            )
            return record, None
        except (ValueError, InvalidOperation, StopIteration) as exc:
            return None, f"Invalid transaction record: {exc}"

    parseAndValidate = parse_and_validate
