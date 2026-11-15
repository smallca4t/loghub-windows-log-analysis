"""Executa o pipeline de parsing, validação, normalização e exportação."""

from pathlib import Path

from export import FIELDNAMES, export_csv
from parser import parse_log
from transformer import normalize_timestamps
from validate import inspect_events, validate_csv

PROJECT_ROOT = Path(__file__).parent.parent
LOG_PATH = PROJECT_ROOT / "data" / "raw" / "Windows_2k.log"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "windows_events_normalized.csv"


def main():
    parsed, failed, total = parse_log(LOG_PATH)
    print(f"Total de linhas: {total}")
    print(f"Linhas parseadas: {len(parsed)}")
    print(f"Linhas não reconhecidas: {len(failed)}")
    if failed:
        print("\nLinhas que precisam de revisão:")
        for event in failed:
            print(f"Linha {event['line_number']}: {event['raw_line']}")

    quality = inspect_events(parsed)
    print("\nNíveis encontrados:")
    for level, count in quality["levels"].items():
        print(f"{level}: {count}")
    print("\nComponentes encontrados:")
    for component, count in quality["components"].items():
        print(f"{component}: {count}")
    print(f"\nMensagens vazias: {quality['empty_messages']}")
    print(f"\nTimestamps inválidos: {len(quality['invalid_timestamps'])}")
    if quality["valid_timestamps"]:
        print(f"Primeiro timestamp: {min(quality['valid_timestamps'])}")
        print(f"Último timestamp: {max(quality['valid_timestamps'])}")
    if quality["invalid_timestamps"]:
        raise ValueError("Há timestamps inválidos; revise-os antes da exportação.")

    events = normalize_timestamps(parsed)
    if events:
        print("\nTipo do timestamp normalizado:", type(events[0]["event_timestamp"]).__name__)

    duplicates = quality["duplicate_lines"]
    print(f"\nPadrões de linha repetidos: {len(duplicates)}")
    print(f"Eventos envolvidos em repetições: {sum(duplicates.values())}")
    print(f"Repetições além da primeira ocorrência: {sum(n - 1 for n in duplicates.values())}")
    if duplicates:
        print("\nExemplos de linhas repetidas:")
        for raw_line, count in list(duplicates.items())[:5]:
            print(f"{count}x: {raw_line}")

    export_csv(events, OUTPUT_PATH)
    print(f"\nArquivo processado criado em: {OUTPUT_PATH}")
    print(f"Eventos exportados: {len(events)}")
    exported_rows = validate_csv(OUTPUT_PATH, FIELDNAMES, len(events))
    print("\nValidação da exportação concluída:")
    print(f"Colunas verificadas: {len(FIELDNAMES)}")
    print(f"Linhas de dados no CSV: {exported_rows}")
    print("Resultado: exportação íntegra.")


if __name__ == "__main__":
    main()
