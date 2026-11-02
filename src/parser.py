from pathlib import Path
import re

LOG_PATH = Path(__file__).parent.parent / "data" / "raw" / "Windows_2k.log"

PATTERN = re.compile(
    r"^(?P<event_timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),"
    r"\s*(?P<level>\S+)"
    r"\s+(?P<component>\S+)"
    r"\s*(?P<message>.*)$"
)

parsed_events = []
failed_events = []

total_lines = 0
parsed_lines = 0
failed_lines = 0

with LOG_PATH.open(encoding="utf-8") as log_file:
    for line_number, raw_line in enumerate(log_file, start=1):
        total_lines += 1

        # Remove apenas a quebra de linha; preserva o restante do conteúdo.
        line = raw_line.rstrip("\r\n")

        match = PATTERN.match(line)

        if match:
            event = {
                "line_number": line_number,
                "raw_line": line,
                "parse_status": "parsed",
                **match.groupdict()
            }

            parsed_events.append(event)
            parsed_lines += 1

        else:
            failed_event = {
                "line_number": line_number,
                "raw_line": line,
                "parse_status": "failed"
            }

            failed_events.append(failed_event)
            failed_lines += 1

print(f"Total de linhas: {total_lines}")
print(f"Linhas parseadas: {parsed_lines}")
print(f"Linhas não reconhecidas: {failed_lines}")

if failed_events:
    print("\nLinhas que precisam de revisão:")
    for event in failed_events:
        print(f"Linha {event['line_number']}: {event['raw_line']}")