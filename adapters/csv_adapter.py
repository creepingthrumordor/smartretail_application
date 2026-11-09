import csv
from smartretail.core.domain import RawRecord
from smartretail.core.exceptions import InputFormatError
from .base import IInputAdapter
class CsvInputAdapter(IInputAdapter):
    def open(self,path):
        try:
            self._file=open(path,encoding='utf-8-sig',newline=''); self._reader=csv.reader(self._file); self._line=0
            next(self._reader,None); self._line=self._reader.line_num
        except OSError as exc: raise InputFormatError(f'Cannot open input file: {exc}') from exc
    def read_chunk(self,size):
        if size<1: raise ValueError('Chunk size must be positive')
        rows=[]
        for _ in range(size):
            try: row=next(self._reader)
            except StopIteration: break
            self._line=self._reader.line_num
            import io
            buffer=io.StringIO(newline=''); csv.writer(buffer).writerow(row)
            rows.append(RawRecord(self._file.name,self._line,buffer.getvalue().rstrip('\r\n')))
        return rows
    def close(self):
        if getattr(self,'_file',None): self._file.close(); self._file=None
