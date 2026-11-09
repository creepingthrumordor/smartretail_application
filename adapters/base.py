from abc import ABC,abstractmethod
class IInputAdapter(ABC):
    @abstractmethod
    def open(self,path:str)->None:...
    @abstractmethod
    def read_chunk(self,size:int):...
    @abstractmethod
    def close(self)->None:...
    def __enter__(self): return self
    def __exit__(self,*args): self.close()
