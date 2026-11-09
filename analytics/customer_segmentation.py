from collections import defaultdict
from .base import IAnalyticsStrategy
from smartretail.core.domain import AnalyticsResult
class CustomerSegmentationStrategy(IAnalyticsStrategy):
 def __init__(self):super().__init__();self.customers=defaultdict(lambda:[0,0])
 def consume(self,records):
  super().consume(records)
  for r in records:
   if r.customer_id:self.customers[r.customer_id][0]+=1;self.customers[r.customer_id][1]+=r.total_amount
 def build_result(self):
  tiers={'Frequent Customers':0,'Occasional Customers':0,'One-Time Customers':0,'Unknown Customers':self.records-sum(x[0] for x in self.customers.values())}
  for n,spend in self.customers.values():tiers['Frequent Customers' if n>=10 or spend>=500 else 'Occasional Customers' if n>1 else 'One-Time Customers']+=1
  return AnalyticsResult(type(self).__name__,{'records':self.records,'segments':tiers},{'segments':[{'segment':k,'customers':v} for k,v in tiers.items()]})
