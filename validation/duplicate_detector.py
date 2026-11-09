from dataclasses import asdict
import hashlib,json
class DuplicateDetector:
    def __init__(self): self._seen={}; self.duplicates=0
    def check(self,record):
        payload=asdict(record); payload.pop('transaction_datetime',None); payload['transaction_datetime']=record.transaction_datetime.isoformat()
        digest=hashlib.sha256(json.dumps(payload,sort_keys=True,default=str).encode()).hexdigest()
        old=self._seen.get(record.transaction_id)
        if old is None:self._seen[record.transaction_id]=digest;return 'new'
        if old==digest:self.duplicates+=1;return 'duplicate'
        return 'conflict'
    def is_duplicate(self,record): return self.check(record)=='duplicate'
