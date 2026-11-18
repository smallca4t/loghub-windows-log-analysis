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

-- 4. Subgrupos provisórios pelo início do nome do pacote.
-- "Outros" preserva mensagens que não se encaixam nos quatro modelos.
-- Resultado: Package_for_KB=541/271, Microsoft-Hyper-V=8/4,
-- Microsoft-Windows=8/4, Package_for_RollupFix=1/1
-- (eventos/mensagens diferentes). A soma é 558/280; Outros=0.
WITH familia AS (
    SELECT message
    FROM public.log_events
    WHERE source_file = 'Windows_2k.log'
      AND message LIKE 'Read out cached package applicability for package:%'
), classificados AS (
    SELECT
        message,
        CASE
            WHEN message LIKE 'Read out cached package applicability for package: Package_for_KB%'
                THEN 'Package_for_KB'
            WHEN message LIKE 'Read out cached package applicability for package: Package_for_RollupFix%'
                THEN 'Package_for_RollupFix'
            WHEN message LIKE 'Read out cached package applicability for package: Microsoft-Windows%'
                THEN 'Microsoft-Windows'
            WHEN message LIKE 'Read out cached package applicability for package: Microsoft-Hyper-V%'
                THEN 'Microsoft-Hyper-V'
            ELSE 'Outros'
        END AS grupo
    FROM familia
)
SELECT
    grupo,
    COUNT(*) AS eventos,
    COUNT(DISTINCT message) AS mensagens_diferentes
FROM classificados
GROUP BY grupo
ORDER BY eventos DESC, grupo;

-- 5. Combinações de ApplicableState e CurrentState na mesma família.
-- O padrão exige os dois números no fim da mensagem.
-- "não extraído" sinaliza mensagens fora desse formato para revisão.
-- Observado (par: eventos/mensagens diferentes): 112/112: 409/205;
-- 80/112: 81/41; 80/0: 26/13; 0/0: 22/11;
-- 112/0: 18/9; 64/0: 2/1. Totais: 558/280; não extraídos: 0.
WITH familia AS (
    SELECT
        message,
        regexp_match(
            message,
            'ApplicableState:[[:space:]]*([0-9]+),[[:space:]]*CurrentState:[[:space:]]*([0-9]+)[[:space:]]*$'
        ) AS estados
    FROM public.log_events
    WHERE source_file = 'Windows_2k.log'
      AND message LIKE 'Read out cached package applicability for package:%'
), extraidos AS (
    SELECT
        message,
        COALESCE(estados[1], 'não extraído') AS applicable_state,
        COALESCE(estados[2], 'não extraído') AS current_state
    FROM familia
)
SELECT
    applicable_state,
    current_state,
    COUNT(*) AS eventos,
    COUNT(DISTINCT message) AS mensagens_diferentes
FROM extraidos
GROUP BY applicable_state, current_state
ORDER BY eventos DESC, applicable_state, current_state;
