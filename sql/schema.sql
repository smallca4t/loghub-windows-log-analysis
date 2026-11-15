-- Eventos estruturados a partir dos logs Windows.
-- Os horários não têm fuso conhecido no arquivo de origem.

CREATE TABLE log_events (
    event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_file TEXT NOT NULL,
    line_number INTEGER NOT NULL CHECK (line_number > 0),
    event_timestamp_raw TEXT NOT NULL,
    event_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    level TEXT NOT NULL,
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    raw_line TEXT NOT NULL,
    parse_status TEXT NOT NULL
);

