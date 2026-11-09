"""Line-oriented adapter for semi-structured log input."""

from typing import TextIO

from smartretail.core.domain import RawRecord
from .base import IInputAdapter


class LogInputAdapter(IInputAdapter):
    """Yield raw log lines in bounded chunks."""

    def __init__(self) -> None:
        self._file: TextIO | None = None
        self._line = 0

    def open(self, path: str) -> None:
        self._file = open(path, encoding="utf-8", errors="replace")
        self._line = 0

    def read_chunk(self, size: int) -> list[RawRecord]:
        records: list[RawRecord] = []
        if self._file is None:
            raise RuntimeError("Open the log adapter before reading")

        for _ in range(size):
            line = self._file.readline()
            if not line:
                break
            self._line += 1
            records.append(
                RawRecord(
                    source=self._file.name,
                    line_number=self._line,
                    data=line.rstrip("\n"),
                )
            )
        return records

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
