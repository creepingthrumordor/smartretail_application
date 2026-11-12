import csv
from smartretail.adapters.csv_adapter import CsvInputAdapter
from smartretail.core.domain import RawRecord
from smartretail.validation.validator import RecordValidator

def test_csv_adapter_reads_in_chunks_and_preserves_quoted_commas(tmp_path):
    path=tmp_path/'quoted.csv'
    path.write_text(
        'id,name\n1,"Rice, basmati"\n2,Tea\n3,Milk\n4,Bread\n5,Apples\n',
        encoding='utf-8',
    )
    adapter=CsvInputAdapter();adapter.open(str(path))
    try:
        first=adapter.read_chunk(2)
        second=adapter.read_chunk(2)
        last=adapter.read_chunk(2)
    finally:adapter.close()
    assert [len(chunk) for chunk in (first, second, last)] == [2, 2, 1]
    assert [row.data.split(",")[0] for row in first + second + last] == [
        "1", "2", "3", "4", "5"
    ]
    assert next(csv.reader([first[0].data]))==['1','Rice, basmati']
    assert first[0].line_number==2

def test_validator_keeps_optional_values_and_defaults_payment(transaction_row):
    transaction_row.update(customer_id='',customer_age='',customer_gender='',customer_city='',discount_percent='',payment_method='')
    raw=RawRecord('fixture.csv',2,','.join(transaction_row.values()))
    record,error=RecordValidator().parse_and_validate(raw)
    assert error is None
    assert record.customer_id is None and record.customer_age is None
    assert record.discount_percent is None
    assert record.payment_method=='Unknown'

def test_validator_rejects_negative_sale_price(transaction_row):
    transaction_row['unit_price']='-10'
    raw=RawRecord('fixture.csv',2,','.join(transaction_row.values()))
    record,error=RecordValidator().parse_and_validate(raw)
    assert record is None
    assert 'Negative unit price' in error
