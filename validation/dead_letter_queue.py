import csv,threading
from smartretail.core.adts import CleanQueue
from smartretail.core.domain import DLQRecord
class DeadLetterQueue:
    def __init__(self): self._queue=CleanQueue(); self._lock=threading.Lock()
    def add(self,record,reason=None):
        if not isinstance(record,DLQRecord): raise TypeError('add expects DLQRecord')
        with self._lock:self._queue.enqueue(record)
    def get_all(self):
        with self._lock:return list(self._queue._items)
    def list_issues(self):return self.get_all()
    def count(self):
        with self._lock:return len(self._queue)
    def export_csv(self,dest_path):
        with open(dest_path,'w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(['source','line_number','raw_data','reason','timestamp']);w.writerows((x.source,x.line_number,x.raw_data,x.reason,x.timestamp.isoformat()) for x in self.get_all())
