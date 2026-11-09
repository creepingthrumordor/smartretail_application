"""Thread-safe quarantine storage for invalid and conflicting records."""

import csv
import threading
from smartretail.core.adts import CleanQueue
from smartretail.core.domain import DLQRecord
class DeadLetterQueue:
    """Store and inspect records rejected by the processing service."""

    def __init__(self) -> None:
        self._queue: CleanQueue[DLQRecord] = CleanQueue()
        self._lock = threading.Lock()

    def add(self, record: DLQRecord, reason: str | None = None) -> None:
        if not isinstance(record, DLQRecord):
            raise TypeError("add expects DLQRecord")
        with self._lock:
            self._queue.enqueue(record)

    def get_all(self) -> list[DLQRecord]:
        with self._lock:
            return self._queue.snapshot()

    def list_issues(self) -> list[DLQRecord]:
        return self.get_all()

    def count(self) -> int:
        with self._lock:
            return len(self._queue)

    def export_csv(self, dest_path: str) -> None:
        with open(dest_path, "w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(["source", "line_number", "raw_data", "reason", "timestamp"])
            writer.writerows(
                (
                    record.source,
                    record.line_number,
                    record.raw_data,
                    record.reason,
                    record.timestamp.isoformat(),
                )
                for record in self.get_all()
            )
