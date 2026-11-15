-- Execute uma vez na tabela já criada, após verificar que não há pares repetidos.
-- Se houver pares (source_file, line_number) duplicados, o ALTER TABLE falhará.
ALTER TABLE public.log_events
ADD CONSTRAINT log_events_source_line_unique UNIQUE (source_file, line_number);
