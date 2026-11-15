"""Inspeciona a qualidade dos dados e confere o CSV gravado."""

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

from transformer import TIMESTAMP_FORMAT


def inspect_events(events):
    valid_timestamps, invalid_timestamps = [], []
    for event in events:
        try:
            valid_timestamps.append(datetime.strptime(
                event["event_timestamp"], TIMESTAMP_FORMAT
            ))
        except ValueError:
            invalid_timestamps.append(event)
    duplicate_lines = {
        line: count
        for line, count in Counter(event["raw_line"] for event in events).items()
        if count > 1
    }
    return {
        "levels": Counter(event["level"] for event in events),
        "components": Counter(event["component"] for event in events),
        "empty_messages": sum(not event["message"].strip() for event in events),
        "valid_timestamps": valid_timestamps,
        "invalid_timestamps": invalid_timestamps,
        "duplicate_lines": duplicate_lines,
    }


def validate_csv(output_path: Path, fieldnames, expected_rows: int):
    with output_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        exported_fieldnames = reader.fieldnames
        exported_rows = sum(1 for _ in reader)
    if exported_fieldnames != fieldnames:
        raise ValueError("As colunas do CSV não correspondem ao esquema esperado.")
    if exported_rows != expected_rows:
        raise ValueError(
            "A quantidade de linhas no CSV não corresponde aos eventos parseados."
        )
    return exported_rows
