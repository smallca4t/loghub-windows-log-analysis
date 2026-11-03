from pathlib import Path
import re
from collections import Counter
from datetime import datetime


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

level_counts = Counter(event["level"] for event in parsed_events)
component_counts = Counter(event["component"] for event in parsed_events)

empty_messages = sum(
    not event["message"].strip()
    for event in parsed_events
)

print("\nNíveis encontrados:")
for level, count in level_counts.items():
    print(f"{level}: {count}")

print("\nComponentes encontrados:")
for component, count in component_counts.items():
    print(f"{component}: {count}")

print(f"\nMensagens vazias: {empty_messages}")

timestamp_format = "%Y-%m-%d %H:%M:%S"

valid_timestamps = []
invalid_timestamps = []

for event in parsed_events:
    try:
        timestamp = datetime.strptime(
            event["event_timestamp"],
            timestamp_format
        )
        valid_timestamps.append(timestamp)

    except ValueError:
        invalid_timestamps.append(event)

print(f"\nTimestamps inválidos: {len(invalid_timestamps)}")

if valid_timestamps:
    print(f"Primeiro timestamp: {min(valid_timestamps)}")
    print(f"Último timestamp: {max(valid_timestamps)}")


raw_line_counts = Counter(
    event["raw_line"]
    for event in parsed_events
)

duplicate_lines = {
    raw_line: count
    for raw_line, count in raw_line_counts.items()
    if count > 1
}

repeated_events = sum(duplicate_lines.values())
extra_repetitions = sum(
    count - 1
    for count in duplicate_lines.values()
)

print(f"\nPadrões de linha repetidos: {len(duplicate_lines)}")
print(f"Eventos envolvidos em repetições: {repeated_events}")
print(f"Repetições além da primeira ocorrência: {extra_repetitions}")

if duplicate_lines:
    print("\nExemplos de linhas repetidas:")
    for raw_line, count in list(duplicate_lines.items())[:5]:
        print(f"{count}x: {raw_line}")