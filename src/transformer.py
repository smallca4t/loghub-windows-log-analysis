"""Converte timestamps sem perder o texto original."""

from datetime import datetime

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def normalize_timestamps(events):
    normalized_events = []
    for event in events:
        normalized = event.copy()
        normalized["event_timestamp_raw"] = event["event_timestamp"]
        normalized["event_timestamp"] = datetime.strptime(
            event["event_timestamp"], TIMESTAMP_FORMAT
        )
        normalized_events.append(normalized)
    return normalized_events
