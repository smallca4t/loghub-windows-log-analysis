"""Exporta eventos normalizados em CSV."""

import csv
from pathlib import Path

from transformer import TIMESTAMP_FORMAT

FIELDNAMES = [
    "line_number", "source_file", "event_timestamp_raw", "event_timestamp",
    "level", "component", "message", "raw_line", "parse_status",
]


def export_csv(events, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open(mode="w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        for event in events:
            export_event = event.copy()
            export_event["event_timestamp"] = event["event_timestamp"].strftime(
                TIMESTAMP_FORMAT
            )
            writer.writerow(export_event)
