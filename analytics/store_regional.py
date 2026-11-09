from collections import defaultdict
from .base import IAnalyticsStrategy
from smartretail.core.domain import AnalyticsResult
class StoreRegionalPerformanceStrategy(IAnalyticsStrategy):
 def __init__(self):super().__init__();self.stores=defaultdict(lambda:[0,0,0,0]);self.regions=defaultdict(lambda:[0,0])
 def consume(self,records):
  super().consume(records)
  for r in records:
   a=self.stores[r.store_id];a[0]+=r.total_amount;a[1]+=1;a[2]+=r.stock_on_hand;a[3]+=r.reorder_level
   b=self.regions[r.region];b[0]+=r.total_amount;b[1]+=1
 def build_result(self):return AnalyticsResult(type(self).__name__,{'records':self.records,'net_revenue':str(self.revenue)},{'stores':[{'store_id':k,'revenue':str(v[0]),'transactions':v[1],'stock_to_reorder':v[2]/v[3] if v[3] else None} for k,v in sorted(self.stores.items(),key=lambda x:x[1][0],reverse=True)],'regions':[{'region':k,'revenue':str(v[0]),'transactions':v[1]} for k,v in self.regions.items()]})
