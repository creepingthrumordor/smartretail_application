from smartretail.core.domain import RawRecord
from .base import IInputAdapter
class LogInputAdapter(IInputAdapter):
    def open(self,path): self._file=open(path,encoding='utf-8',errors='replace'); self._line=0
    def read_chunk(self,size):
        out=[]
        for _ in range(size):
            line=self._file.readline()
            if not line: break
            self._line+=1; out.append(RawRecord(self._file.name,self._line,line.rstrip('\n')))
        return out
    def close(self):
        if getattr(self,'_file',None):self._file.close();self._file=None
