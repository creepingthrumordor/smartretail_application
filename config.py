"""Application defaults and transaction schema."""
CSV_FIELDS = ["transaction_id","transaction_datetime","store_id","store_city","region","warehouse_id","customer_id","customer_age","customer_gender","customer_city","product_category","product_name","quantity","unit_price","discount_percent","promotion_name","payment_method","channel","total_amount","stock_on_hand","reorder_level","transaction_type"]
DEFAULT_CHUNK_SIZE = 5000
ANALYSES = ("peak_sales", "customer_segmentation", "seasonal_demand", "product_revenue", "anomaly_detection", "store_regional_performance")
