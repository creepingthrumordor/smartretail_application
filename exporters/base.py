"""Exporter interface for analytics results."""

from abc import ABC, abstractmethod

from smartretail.core.domain import AnalyticsResult


class IResultExporter(ABC):
    """Write an analysis result to a destination."""

    @abstractmethod
    def export(self, result: AnalyticsResult, destination: str) -> str | None:
        raise NotImplementedError
