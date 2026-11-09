from collections import Counter
from .base import IAnalyticsStrategy
from smartretail.core.domain import AnalyticsResult
class SeasonalDemandStrategy(IAnalyticsStrategy):
 def __init__(self):super().__init__();self.months=Counter();self.promos=Counter()
 def consume(self,records):
  super().consume(records)
  for r in records:self.months[r.transaction_datetime.month]+=r.total_amount;self.promos[r.promotion_name or 'None']+=r.total_amount
 def build_result(self):return AnalyticsResult(type(self).__name__,{'records':self.records,'net_revenue':str(self.revenue)},{'monthly_revenue':[{'month':m,'revenue':str(self.months[m])} for m in range(1,13)],'promotions':[{'promotion':k,'revenue':str(v)} for k,v in self.promos.items()]})
