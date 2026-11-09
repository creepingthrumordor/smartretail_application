"""Small, encapsulated abstract data types used by the application."""

from collections import deque
from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class CleanQueue(Generic[T]):
    """FIFO queue with safe empty-queue operations."""

    def __init__(self) -> None:
        self._items: deque[T] = deque()

    def enqueue(self, item: T) -> None:
        self._items.append(item)

    def dequeue(self) -> T | None:
        return self._items.popleft() if self._items else None

    def peek(self) -> T | None:
        return self._items[0] if self._items else None

    def snapshot(self) -> list[T]:
        """Return a copy without exposing the queue's internal container."""
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)


class CleanRegistry(Generic[K, V]):
    """Hash-map wrapper with a guard against invalid keys."""

    def __init__(self) -> None:
        self._items: dict[K, V] = {}

    def set(self, key: K, value: V) -> None:
        if key is None:
            raise ValueError("Registry key cannot be None")
        self._items[key] = value

    def get(self, key: K, default: V | None = None) -> V | None:
        return self._items.get(key, default)

    def contains(self, key: K) -> bool:
        return key in self._items

    def items(self) -> Iterator[tuple[K, V]]:
        return iter(self._items.items())

    def __len__(self) -> int:
        return len(self._items)


class CleanMergeSort:
    """Stable merge sort with O(n log n) time complexity."""

    @staticmethod
    def sort(
        values: list[T],
        key: Callable[[T], object] = lambda item: item,
        reverse: bool = False,
    ) -> list[T]:
        if len(values) < 2:
            return list(values)

        midpoint = len(values) // 2
        left = CleanMergeSort.sort(values[:midpoint], key, reverse)
        right = CleanMergeSort.sort(values[midpoint:], key, reverse)
        return CleanMergeSort._merge(left, right, key, reverse)

    @staticmethod
    def _merge(
        left: list[T],
        right: list[T],
        key: Callable[[T], object],
        reverse: bool,
    ) -> list[T]:
        merged: list[T] = []
        left_index = right_index = 0

        while left_index < len(left) and right_index < len(right):
            left_key = key(left[left_index])
            right_key = key(right[right_index])
            take_left = left_key >= right_key if reverse else left_key <= right_key
            if take_left:
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1

        merged.extend(left[left_index:])
        merged.extend(right[right_index:])
        return merged


class CleanBinarySearch:
    """Boundary-safe binary search for an already-sorted list."""

    @staticmethod
    def search(values: list[T], target: T) -> int:
        low, high = 0, len(values) - 1
        while low <= high:
            midpoint = low + ((high - low) // 2)
            if values[midpoint] == target:
                return midpoint
            if values[midpoint] < target:
                low = midpoint + 1
            else:
                high = midpoint - 1
        return -1
