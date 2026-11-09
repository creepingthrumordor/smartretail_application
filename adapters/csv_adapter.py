"""CSV implementation of the source-agnostic input adapter."""

import csv
import io
from _csv import Reader
from typing import TextIO

from smartretail.core.domain import RawRecord
from smartretail.core.exceptions import InputFormatError
from .base import IInputAdapter


class CsvInputAdapter(IInputAdapter):
    """Read CSV data rows incrementally while retaining source line numbers."""

    def __init__(self) -> None:
        self._file: TextIO | None = None
        self._reader: Reader | None = None
        self._line = 0

    def open(self, path: str) -> None:
        try:
            self._file = open(path, encoding="utf-8-sig", newline="")
            self._reader = csv.reader(self._file)
            next(self._reader, None)  # First row is the header.
            self._line = self._reader.line_num
        except OSError as exc:
            raise InputFormatError(f"Cannot open input file: {exc}") from exc

    def read_chunk(self, size: int) -> list[RawRecord]:
        if size < 1:
            raise ValueError("Chunk size must be positive")
        if self._reader is None or self._file is None:
            raise RuntimeError("Open the CSV adapter before reading")

        records: list[RawRecord] = []
        for _ in range(size):
            try:
                row = next(self._reader)
            except StopIteration:
                break

            self._line = self._reader.line_num
            buffer = io.StringIO(newline="")
            csv.writer(buffer).writerow(row)
            records.append(
                RawRecord(
                    source=self._file.name,
                    line_number=self._line,
                    data=buffer.getvalue().rstrip("\r\n"),
                )
            )
        return records

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
            self._reader = None
