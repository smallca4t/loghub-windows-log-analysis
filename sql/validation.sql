-- Conferência da primeira carga de Windows_2k.log.
-- Os valores esperados abaixo valem para o dataset atual de 2.000 eventos.
-- Execute conectado ao banco loghub_windows_logs após a importação.

-- Pré-requisito da migração 001: esta consulta deve retornar zero linhas.
SELECT source_file, line_number, COUNT(*) AS ocorrencias
FROM public.log_events
GROUP BY source_file, line_number
HAVING COUNT(*) > 1;

-- 1. Quantidade, cobertura das linhas e período.
-- Esperado: total=2000; linhas_distintas=2000; primeira_linha=1;
-- ultima_linha=2000; primeiro_evento=2016-09-28 04:30:30;
-- ultimo_evento=2016-09-29 02:04:40.
SELECT
    COUNT(*) AS total,
    COUNT(DISTINCT line_number) AS linhas_distintas,
    MIN(line_number) AS primeira_linha,
    MAX(line_number) AS ultima_linha,
    MIN(event_timestamp) AS primeiro_evento,
    MAX(event_timestamp) AS ultimo_evento
FROM public.log_events
WHERE source_file = 'Windows_2k.log';

-- 2. Distribuição dos campos estruturados.
-- Esperado: CBS/Info=1973; CSI/Info=27.
SELECT component, level, COUNT(*) AS eventos
FROM public.log_events
WHERE source_file = 'Windows_2k.log'
GROUP BY component, level
ORDER BY eventos DESC;
