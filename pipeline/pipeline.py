class ProcessingPipeline:
 def __init__(self,steps=()):self.steps=tuple(steps)
 def process_chunk(self,records):
  for step in self.steps:records=step.apply(records)
  return records
