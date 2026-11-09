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

Click the preview to open the video, where playback can be started and paused:

<p align="center">
  <a href="demo.mp4">
    <img src="showcase.png" alt="Open the SmartRetail demo video" width="1000" />
  </a>
</p>

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

