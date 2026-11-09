"""Interface for input sources that produce raw records in chunks."""

from abc import ABC, abstractmethod

from smartretail.core.domain import RawRecord


class IInputAdapter(ABC):
    """Lifecycle and chunk-reading contract for input adapters."""

    @abstractmethod
    def open(self, path: str) -> None:
        """Open a source for reading."""
        raise NotImplementedError

    @abstractmethod
    def read_chunk(self, size: int) -> list[RawRecord]:
        """Return up to ``size`` records, or an empty list at end of input."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Release the input source."""
        raise NotImplementedError

    def __enter__(self) -> "IInputAdapter":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
