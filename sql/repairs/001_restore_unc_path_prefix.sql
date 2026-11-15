-- Repara a importação inicial do CSV nas linhas 977 a 984.
-- O importador interpretou a primeira dupla de barras do caminho UNC
-- como uma barra única, tanto em raw_line quanto em message.
-- Execute uma vez no banco loghub_windows_logs, após revisar o escopo.
-- O bloco DO é atômico: qualquer erro cancela todas as alterações dele.

DO $repair$
DECLARE
    affected_rows INTEGER;
    source_prefix TEXT := chr(92) || '?' || chr(92) || 'GLOBALROOT';
    expected_prefix TEXT := chr(92) || chr(92) || '?' || chr(92) || 'GLOBALROOT';
BEGIN
    IF (
        SELECT COUNT(*)
        FROM public.log_events
        WHERE source_file = 'Windows_2k.log'
          AND line_number BETWEEN 977 AND 984
          AND position(source_prefix IN raw_line) > 0
          AND position(source_prefix IN message) > 0
          AND position(expected_prefix IN raw_line) = 0
          AND position(expected_prefix IN message) = 0
    ) <> 8 THEN
        RAISE EXCEPTION 'Os oito registros não estão no estado esperado; nenhuma linha foi alterada';
    END IF;

    UPDATE public.log_events
    SET raw_line = replace(raw_line, source_prefix, expected_prefix),
        message = replace(message, source_prefix, expected_prefix)
    WHERE source_file = 'Windows_2k.log'
      AND line_number BETWEEN 977 AND 984;

    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    IF affected_rows <> 8 THEN
        RAISE EXCEPTION 'Esperadas 8 alterações; obtidas %. Operação cancelada', affected_rows;
    END IF;
END
$repair$;

-- Esperado: oito linhas com true nas duas colunas.
SELECT line_number,
       (position(chr(92) || chr(92) || '?' IN raw_line) > 0)::text
           AS raw_tem_duas_barras,
       (position(chr(92) || chr(92) || '?' IN message) > 0)::text
           AS mensagem_tem_duas_barras
FROM public.log_events
WHERE source_file = 'Windows_2k.log'
  AND line_number BETWEEN 977 AND 984
ORDER BY line_number;
