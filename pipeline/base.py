from abc import ABC,abstractmethod
class ITransformation(ABC):
 @abstractmethod
 def apply(self,records):...
