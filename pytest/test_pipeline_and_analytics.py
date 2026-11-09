from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from smartretail.analytics.peak_sales import PeakSalesStrategy
from smartretail.analytics.anomaly_detection import AnomalyDetectionStrategy
from smartretail.core.domain import TransactionRecord
from smartretail.pipeline.builder import PipelineBuilder

def make_record(transaction_id, hour, discount=None):
    return TransactionRecord(transaction_id,datetime(2024,5,21,hour,0),'STR001','Colombo','West','WH001',
        'CUS001',30,'F','Colombo','Groceries','Rice',2,Decimal('100'),
        Decimal(str(discount)) if discount is not None else None,None,'Cash','In-Store',Decimal('180'),20,5,'Sale',False)

def test_builder_applies_filter_then_enrichment():
    records=[make_record('a',9),make_record('b',17)]
    pipeline=(PipelineBuilder().add_filter(lambda row:row.transaction_datetime.hour>=12)
              .add_enrichment(lambda row:replace(row,product_name=row.product_name.upper())).build())
    output=pipeline.process_chunk(records)
    assert len(output)==1
    assert output[0].product_name=='RICE'

def test_peak_sales_strategy_counts_hour_and_weekday():
    strategy=PeakSalesStrategy();strategy.consume([make_record('a',17),make_record('b',17),make_record('c',9)])
    result=strategy.build_result()
    assert result.summary['records']==3
    assert result.charts_data['heatmap'][17][1]==2  # May 21, 2024 is Tuesday

def test_anomaly_strategy_reports_extreme_discount():
    strategy=AnomalyDetectionStrategy();strategy.consume([make_record('a',17,50)])
    result=strategy.build_result()
    assert result.summary['discount_spikes']==1
    assert result.tables['alert_breakdown']==[{'alert_type':'Extreme discount','count':1}]
