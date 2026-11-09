"""Domain exceptions surfaced at application boundaries."""


class SmartRetailError(Exception):
    """Base exception for application-level failures."""


class InputFormatError(SmartRetailError):
    """Input file or requested input configuration is invalid."""


class ExportError(SmartRetailError):
    """An analysis result could not be exported."""
