from pathlib import Path
import re

LOG_PATH = Path(__file__).parent.parent / "data" / "raw" / "amostras.log"

PATTERN = re.compile(
    r"^(?P<event_timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),"
    r"\s*(?P<level>\S+)"
    r"\s+(?P<component>\S+)"
    r"\s*(?P<message>.*)$"
)

with LOG_PATH.open(encoding="utf-8") as log_file:
    for line_number, raw_line in enumerate(log_file, start=1):
        line = raw_line.rstrip("\n")
        match = PATTERN.match(line)

        if match:
            event = match.groupdict()
            print(event)
        else:
            print(f"Linha {line_number} não reconhecida: {line}")