from collections import Counter
from .base import IAnalyticsStrategy
from smartretail.core.domain import AnalyticsResult
class PeakSalesStrategy(IAnalyticsStrategy):
 def __init__(self):super().__init__();self.hours=Counter();self.stores=Counter()
 def consume(self,records):
  super().consume(records)
  for r in records:self.hours[(r.transaction_datetime.hour,r.transaction_datetime.weekday())]+=1;self.stores[r.store_id]+=1
 def build_result(self):return AnalyticsResult(type(self).__name__,{'records':self.records,'net_revenue':str(self.revenue)}, {'peak_hours':[{'hour':h,'weekday':d,'count':n} for (h,d),n in self.hours.most_common()], 'stores':[{'store_id':s,'transactions':n} for s,n in self.stores.most_common()]},{'heatmap':[[self.hours[(h,d)] for d in range(7)] for h in range(24)]})
