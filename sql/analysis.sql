-- Análise exploratória de Windows_2k.log.
-- Execute conectado ao banco loghub_windows_logs após a carga.
-- Os resultados anotados correspondem aos 2.000 eventos analisados.

-- 1. Mensagens completas repetidas: a igualdade inclui todo o texto.
-- A mensagem mais frequente é
-- "Warning: Unrecognized packageExtended attribute." (280 ocorrências).
SELECT message, COUNT(*) AS ocorrencias
FROM public.log_events
WHERE source_file = 'Windows_2k.log'
GROUP BY message
HAVING COUNT(*) > 1
ORDER BY ocorrencias DESC, message
LIMIT 10;

-- 2. Família definida pelo início da mensagem, mesmo com sufixos diferentes.
-- Resultado observado: 558 ocorrências; 280 mensagens completas diferentes.
-- COUNT(DISTINCT message) não equivale a contar pacotes distintos.
SELECT
    COUNT(*) AS total_ocorrencias,
    COUNT(DISTINCT message) AS mensagens_diferentes
FROM public.log_events
WHERE source_file = 'Windows_2k.log'
  AND message LIKE 'Read out cached package applicability for package:%';

-- 3. Frequência de cada mensagem completa dentro da família.
-- O mesmo texto em eventos diferentes não implica eventos duplicados.
-- Pelos totais e pela ordem observada: 3 textos ocorrem 4 vezes,
-- 269 ocorrem 2 vezes e 8 ocorrem 1 vez (558 eventos ao todo).
SELECT
    message,
    COUNT(*) AS ocorrencias
FROM public.log_events
WHERE source_file = 'Windows_2k.log'
  AND message LIKE 'Read out cached package applicability for package:%'
GROUP BY message
ORDER BY ocorrencias DESC, message
LIMIT 20;
