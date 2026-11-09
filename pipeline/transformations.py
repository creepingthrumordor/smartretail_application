from .base import ITransformation
class FilterTransformation(ITransformation):
 def __init__(self,predicate):self.predicate=predicate
 def apply(self,records):return [r for r in records if self.predicate(r)]
class EnrichmentTransformation(ITransformation):
 def __init__(self,enricher_func):self.enricher_func=enricher_func
 def apply(self,records):return [self.enricher_func(r) for r in records]
class AggregationTransformation(ITransformation):
 def __init__(self,agg_func):self.agg_func=agg_func
 def apply(self,records):return self.agg_func(records)
