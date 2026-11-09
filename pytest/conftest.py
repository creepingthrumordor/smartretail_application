"""Shared pytest fixtures and project import setup."""
import sys
from pathlib import Path

TEST_LOCATION = Path(__file__).resolve()
PROJECT_ROOT = next(
    (parent for parent in TEST_LOCATION.parents if (parent / 'smartretail' / '__init__.py').is_file()),
    None,
)
if PROJECT_ROOT is None:
    PROJECT_ROOT = next(
        (parent.parent for parent in TEST_LOCATION.parents
         if parent.name == 'smartretail' and (parent / '__init__.py').is_file()),
        TEST_LOCATION.parents[2],
    )
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from smartretail.config import CSV_FIELDS

@pytest.fixture
def transaction_row():
    """A complete valid transaction using the application's CSV schema."""
    return {
        'transaction_id': 'TX-TEST-1', 'transaction_datetime': '5/21/2024 17:32',
        'store_id': 'STR001', 'store_city': 'Colombo', 'region': 'West',
        'warehouse_id': 'WH001', 'customer_id': 'CUS001', 'customer_age': '30',
        'customer_gender': 'F', 'customer_city': 'Colombo', 'product_category': 'Groceries',
        'product_name': 'Rice', 'quantity': '2', 'unit_price': '100.00',
        'discount_percent': '10', 'promotion_name': 'Weekend Promo',
        'payment_method': 'Cash', 'channel': 'In-Store', 'total_amount': '180.00',
        'stock_on_hand': '20', 'reorder_level': '5', 'transaction_type': 'Sale',
    }

@pytest.fixture
def write_transactions(tmp_path):
    """Write dictionaries as a correctly quoted 22-column CSV file."""
    import csv
    def write(rows, name='transactions.csv'):
        path=tmp_path/name
        with path.open('w',newline='',encoding='utf-8') as file:
            writer=csv.DictWriter(file,fieldnames=CSV_FIELDS);writer.writeheader();writer.writerows(rows)
        return path
    return write
