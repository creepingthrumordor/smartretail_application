from abc import ABC,abstractmethod
class IResultExporter(ABC):
 @abstractmethod
 def export(self,result,destination):...
