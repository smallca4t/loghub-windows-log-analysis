"""Carga idempotente do CSV processado no PostgreSQL.

Usa PGHOST, PGPORT, PGUSER, PGDATABASE e PGPASSWORD quando definidos.
Sem PGPASSWORD, pede a senha sem exibi-la no terminal.
"""

import csv
from getpass import getpass
import os
from pathlib import Path

import psycopg

from export import FIELDNAMES


PROJECT_ROOT = Path(__file__).parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "windows_events_normalized.csv"
COLUMNS = FIELDNAMES


def load_csv(csv_path: Path = CSV_PATH):
    """Insere linhas novas, ignora as idênticas e rejeita conflitos.

    Uma exceção cancela toda a transação, sem inserir parcialmente o arquivo.
    Execute antes a migração 001 na tabela criada manualmente.
    """
    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames != COLUMNS:
            raise ValueError("O cabeçalho do CSV não corresponde às nove colunas esperadas.")
        rows = list(reader)

    keys = [(row["source_file"], int(row["line_number"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("O CSV contém pares (source_file, line_number) repetidos.")

    inserted = 0
    already_loaded = 0
    missing_rows = []
    conflicts = []
    connection_options = {
        "host": os.environ.get("PGHOST", "localhost"),
        "port": os.environ.get("PGPORT", "5433"),
        "user": os.environ.get("PGUSER", "postgres"),
        "dbname": os.environ.get("PGDATABASE", "loghub_windows_logs"),
        "password": os.environ.get("PGPASSWORD") or getpass("Senha do PostgreSQL: "),
    }
    with psycopg.connect(**connection_options) as connection:
        with connection.cursor() as cursor:
            for row, (source_file, line_number) in zip(rows, keys):
                cursor.execute(
                    "SELECT raw_line FROM public.log_events "
                    "WHERE source_file = %s AND line_number = %s",
                    (source_file, line_number),
                )
                existing = cursor.fetchone()
                if existing is not None:
                    if existing[0] != row["raw_line"]:
                        conflicts.append((source_file, line_number))
                    else:
                        already_loaded += 1
                    continue

                missing_rows.append(row)

            if conflicts:
                examples = ", ".join(
                    f"{source_file}:{line_number}"
                    for source_file, line_number in conflicts[:10]
                )
                raise ValueError(
                    f"{len(conflicts)} conflitos entre CSV e banco. "
                    f"Primeiros pares (arquivo:linha): {examples}. "
                    "Nenhum evento foi inserido."
                )

            for row in missing_rows:
                cursor.execute(
                    "INSERT INTO public.log_events "
                    "(line_number, source_file, event_timestamp_raw, "
                    "event_timestamp, level, component, message, raw_line, parse_status) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    tuple(row[column] for column in COLUMNS),
                )
                inserted += 1

    return inserted, already_loaded


if __name__ == "__main__":
    inserted, already_loaded = load_csv()
    print(f"Eventos inseridos: {inserted}")
    print(f"Eventos já carregados: {already_loaded}")
