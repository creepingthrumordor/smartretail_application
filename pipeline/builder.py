from .pipeline import ProcessingPipeline
from .transformations import FilterTransformation,EnrichmentTransformation,AggregationTransformation
class PipelineBuilder:
 def __init__(self):self._steps=[]
 def add_filter(self,predicate):self._steps.append(FilterTransformation(predicate));return self
 def add_enrichment(self,enricher):self._steps.append(EnrichmentTransformation(enricher));return self
 def add_aggregation(self,aggregator):self._steps.append(AggregationTransformation(aggregator));return self
 def build(self):return ProcessingPipeline(self._steps)
