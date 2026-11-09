class SmartRetailError(Exception): """Base application error."""
class InputFormatError(SmartRetailError): """Invalid or unsupported input."""
class ExportError(SmartRetailError): """Could not export an analysis."""
