"""Detect repeated transaction IDs and distinguish exact row duplicates."""

import hashlib
import json
from dataclasses import asdict

from smartretail.core.domain import TransactionRecord


class DuplicateDetector:
    """Track a stable content digest for each first-seen transaction ID."""

    def __init__(self) -> None:
        self._seen: dict[str, str] = {}
        self.duplicates = 0

    @staticmethod
    def _content_digest(record: TransactionRecord) -> str:
        payload = asdict(record)
        payload["transaction_datetime"] = record.transaction_datetime.isoformat()
        serialized = json.dumps(payload, sort_keys=True, default=str).encode()
        return hashlib.sha256(serialized).hexdigest()

    def check(self, record: TransactionRecord) -> str:
        digest = self._content_digest(record)
        existing_digest = self._seen.get(record.transaction_id)
        if existing_digest is None:
            self._seen[record.transaction_id] = digest
            return "new"
        if existing_digest == digest:
            self.duplicates += 1
            return "duplicate"
        return "conflict"

    def is_duplicate(self, record: TransactionRecord) -> bool:
        return self.check(record) == "duplicate"
