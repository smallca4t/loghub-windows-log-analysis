"""Lê logs e extrai os campos de cada linha."""

from pathlib import Path
import re

PATTERN = re.compile(
    r"^(?P<event_timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),"
    r"\s*(?P<level>\S+)\s+(?P<component>\S+)\s*(?P<message>.*)$"
)


def parse_log(log_path: Path):
    parsed, failed = [], []
    with log_path.open(encoding="utf-8") as log_file:
        for line_number, raw_line in enumerate(log_file, start=1):
            line = raw_line.rstrip("\r\n")
            source = {
                "line_number": line_number,
                "source_file": log_path.name,
                "raw_line": line,
            }
            match = PATTERN.match(line)
            if match:
                parsed.append({**source, "parse_status": "parsed", **match.groupdict()})
            else:
                failed.append({**source, "parse_status": "failed"})
    return parsed, failed, len(parsed) + len(failed)
