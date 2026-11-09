# SmartRetail Analytics

<p align="center">
  <img src="showcase.png" alt="SmartRetail dashboard showcase" width="1000" />
</p>

A Python desktop application for retail transaction ingestion, validation, deduplication, segmentation analytics, and export-ready reporting.

## Highlights

- Chunked CSV ingestion for large retail datasets
- Validation and deduplication for clean transaction data
- Customer segmentation analysis with KPI summaries
- Export to PDF, CSV, and HTML reports
- Lightweight Python-only implementation with a desktop UI

## Demo

<p align="center">
  <a href="demo.mp4">
    <img src="showcase.png" alt="SmartRetail demo preview" width="1000" />
  </a>
</p>

GitHub does not play repository MP4 files inline in a README. [Open or download the demo video](demo.mp4) to watch it with playback controls.

## Run

```bash
python -m pip install -r requirements.txt
python3 main.py
```

## Testing

```bash
python -m pytest -v
```

The analytics engine is built using Python's standard library and is designed for quick retail insight generation from CSV transaction data.

