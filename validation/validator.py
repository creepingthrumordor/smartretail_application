import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from smartretail.config import CSV_FIELDS
from smartretail.core.domain import RawRecord, TransactionRecord
class RecordValidator:
    def parse_and_validate(self,raw:RawRecord):
        try:
            row=next(csv.reader([raw.data]))
            if len(row)!=22: return None,f'Expected 22 fields, received {len(row)}'
            d=dict(zip(CSV_FIELDS,(x.strip() for x in row)))
            if not d['transaction_id']: return None,'Missing transaction_id'
            dt=datetime.strptime(d['transaction_datetime'],'%m/%d/%Y %H:%M')
            qty=int(d['quantity']); typ=d['transaction_type']
            price=Decimal(d['unit_price']); amount=Decimal(d['total_amount'])
            if typ=='Sale' and price<0:return None,'Negative unit price on Sale'
            if typ=='Return' and qty>=0:return None,'Return quantity must be negative'
            age=int(d['customer_age']) if d['customer_age'] else None
            discount=Decimal(d['discount_percent']) if d['discount_percent'] else None
            rec=TransactionRecord(d['transaction_id'],dt,d['store_id'],d['store_city'],d['region'],d['warehouse_id'],d['customer_id'] or None,age,d['customer_gender'] or None,d['customer_city'] or None,d['product_category'],d['product_name'],qty,price,discount,d['promotion_name'] or None,d['payment_method'] or 'Unknown',d['channel'],amount,int(d['stock_on_hand']),int(d['reorder_level']),typ,typ=='Return')
            return rec,None
        except (ValueError,InvalidOperation,StopIteration) as exc:return None,f'Invalid transaction record: {exc}'
    parseAndValidate=parse_and_validate
