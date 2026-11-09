from abc import ABC,abstractmethod
from smartretail.core.domain import AnalyticsResult
class IAnalyticsStrategy(ABC):
 def __init__(self):self.records=0;self.revenue=0
 def consume(self,records):
  self.records+=len(records);self.revenue+=sum((r.total_amount for r in records),start=__import__('decimal').Decimal('0'))
 @abstractmethod
 def build_result(self)->AnalyticsResult:...
