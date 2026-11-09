from collections import deque
from typing import Generic, TypeVar, Callable
T=TypeVar('T'); K=TypeVar('K'); V=TypeVar('V')
class CleanQueue(Generic[T]):
    def __init__(self): self._items=deque()
    def enqueue(self,item:T)->None: self._items.append(item)
    def dequeue(self)->T|None: return self._items.popleft() if self._items else None
    def peek(self)->T|None: return self._items[0] if self._items else None
    def __len__(self): return len(self._items)
class CleanRegistry(Generic[K,V]):
    def __init__(self): self._items={}
    def set(self,key:K,value:V)->None:
        if key is None: raise ValueError('Registry key cannot be None')
        self._items[key]=value
    def get(self,key:K,default=None): return self._items.get(key,default)
    def contains(self,key:K)->bool: return key in self._items
    def items(self): return self._items.items()
    def __len__(self): return len(self._items)
class CleanMergeSort:
    @staticmethod
    def sort(values:list[T], key:Callable[[T],object]=lambda x:x, reverse:bool=False)->list[T]:
        if len(values)<2: return list(values)
        mid=len(values)//2; left=CleanMergeSort.sort(values[:mid],key,reverse); right=CleanMergeSort.sort(values[mid:],key,reverse); out=[]
        while left and right:
            take_left=key(left[0])>=key(right[0]) if reverse else key(left[0])<=key(right[0])
            out.append(left.pop(0) if take_left else right.pop(0))
        return out+left+right
class CleanBinarySearch:
    @staticmethod
    def search(values:list[T], target:T)->int:
        low,high=0,len(values)-1
        while low<=high:
            mid=low+((high-low)//2)
            if values[mid]==target:return mid
            if values[mid]<target:low=mid+1
            else:high=mid-1
        return -1
