from collections import Counter,defaultdict
from .base import IAnalyticsStrategy
from smartretail.core.domain import AnalyticsResult
class ProductRevenueStrategy(IAnalyticsStrategy):
 def __init__(self):super().__init__();self.categories=Counter();self.products=Counter();self.regions=Counter();self.stores=Counter();self.qty=defaultdict(lambda:[0,0])
 def consume(self,records):
  super().consume(records)
  for r in records:
   self.categories[r.product_category]+=r.total_amount;self.products[r.product_name]+=r.total_amount;self.regions[r.region]+=r.total_amount;self.stores[r.store_id]+=r.total_amount;self.qty[r.product_category][0 if r.is_return else 1]+=abs(r.quantity)
 def build_result(self):return AnalyticsResult(type(self).__name__,{'records':self.records,'net_revenue':str(self.revenue)},{k:[{'name':n,'revenue':str(v)} for n,v in c.most_common(20)] for k,c in [('categories',self.categories),('products',self.products),('regions',self.regions),('stores',self.stores)]})
