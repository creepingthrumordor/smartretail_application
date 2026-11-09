from datetime import datetime
from smartretail.core.domain import DLQRecord
from smartretail.validation.validator import RecordValidator
from smartretail.validation.duplicate_detector import DuplicateDetector
class ChunkProcessingService:
 def __init__(self,strategy,dlq,pipeline=None,validator=None,duplicate_detector=None):
  self.strategy=strategy;self.dlq=dlq;self.pipeline=pipeline;self.validator=validator or RecordValidator();self.duplicates=duplicate_detector or DuplicateDetector();self.processed=0
 def process_stream(self,adapter,chunk_size,progress_callback=None):
  while True:
   chunk=adapter.read_chunk(chunk_size)
   if not chunk:break
   valid=[]
   for raw in chunk:
    self.processed+=1;record,error=self.validator.parse_and_validate(raw)
    if error:self.dlq.add(DLQRecord(raw.source,raw.line_number,raw.data,error,datetime.now()));continue
    state=self.duplicates.check(record)
    if state=='duplicate':continue
    if state=='conflict':self.dlq.add(DLQRecord(raw.source,raw.line_number,raw.data,'Conflicting duplicate transaction_id',datetime.now()));continue
    valid.append(record)
   if self.pipeline:valid=self.pipeline.process_chunk(valid)
   self.strategy.consume(valid)
   if progress_callback:progress_callback(0.0,self.processed,self.dlq.count())
  result=self.strategy.build_result();result.summary.update({'total_rows':self.processed,'duplicates':self.duplicates.duplicates,'quarantined':self.dlq.count()});return result
 def run(self,adapter,path,chunk_size,progress_callback=None):
  adapter.open(path)
  try:return self.process_stream(adapter,chunk_size,progress_callback)
  finally:adapter.close()
