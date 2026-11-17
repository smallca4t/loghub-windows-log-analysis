# Ficha de caracterização — Windows_2k.log

## 1. Identificação do dataset

- Arquivo: Windows_2k.log
- Origem declarada: LogHub, disponível no GitHub.
- URL/origem específica: ainda não registrada.
- Formato: .log (texto).
- Tamanho: a confirmar pelas propriedades do arquivo.
- Total de linhas: 2.000.
- Codificação usada na leitura: UTF-8; a leitura Python foi concluída sem erro de decodificação.

## 2. Organização dos registros

- Cada linha física corresponde a um evento de log. A impressão inicial de eventos em múltiplas linhas era efeito de zoom no editor.
- Não foram observadas linhas vazias.
- Os eventos iniciam com timestamp no formato AAAA-MM-DD HH:MM:SS.
- Após o timestamp há uma vírgula, seguida por nível, componente e mensagem.
- A quantidade de espaços entre nível, componente e mensagem varia devido ao alinhamento visual do log.

Padrão identificado: timestamp, nível, componente, mensagem.

## 3. Campos estruturados

- event_timestamp: timestamp principal no início do evento.
- level: nível registrado, por exemplo Info.
- component: componente de origem, por exemplo CBS ou CSI.
- message: texto livre restante do evento.
- line_number: número da linha-fonte para rastreabilidade.
- raw_line: conteúdo original da linha, sem o terminador de linha.
- parse_status: resultado da interpretação, com os valores parsed ou failed.

## 4. Características e limitações

- message é texto semiestruturado e pode conter vírgulas, caminhos Windows, códigos HRESULT, parênteses, GUIDs, números e timestamps internos.
- Vírgulas em message não são separadores de campo; apenas a vírgula após o timestamp pertence ao prefixo reconhecido.
- Timestamps internos da mensagem não devem ser confundidos com event_timestamp.
- A primeira versão não extrai informações semânticas internas das mensagens, como HRESULTs ou nomes de pacotes.

## 5. Estratégia de parsing

O parser lê uma linha por vez e usa a expressão regular:

^(?P<event_timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*(?P<level>\S+)\s+(?P<component>\S+)\s*(?P<message>.*)$

Ela extrai timestamp, nível, componente e mensagem, preservando o restante do texto. Linhas fora do padrão seriam mantidas com parse_status igual a failed; nenhum registro seria descartado silenciosamente.

## 6. Resultado da execução do parser

- Total de linhas lidas: 2.000
- Eventos parseados: 2.000
- Linhas não reconhecidas: 0
- Taxa de parsing: 100,0%

A reconciliação foi satisfeita: total de linhas lidas = eventos parseados + linhas não reconhecidas.

## 7. Validação após o parsing

Foram conferidas as frequências de level e component, mensagens vazias, intervalo temporal, validade dos timestamps e ocorrência de linhas idênticas repetidas. Registros repetidos não foram removidos sem justificativa baseada no contexto do log.

## 8. Resultado da validação inicial

| Verificação | Resultado |
| --- | --- |
| Valores de `level` | `Info`: 2.000 eventos |
| Valores de `component` | `CBS`: 1.973 (98,65%); `CSI`: 27 (1,35%) |
| Mensagens vazias | 0 |
| Timestamps inválidos | 0 |
| Intervalo temporal | 2016-09-28 04:30:30 até 2016-09-29 02:04:40 |
| Padrões de linha repetidos | 23 |
| Eventos envolvidos em repetições | 742 |
| Repetições além da primeira ocorrência | 719 |

A estrutura extraída é coerente com o padrão observado. A presença da palavra `Warning` em algumas mensagens não altera o valor estruturado de `level`, que é `Info` em todos os registros.

As repetições exatas foram preservadas: podem representar ocorrências legítimas do processo registrado. Uma eventual deduplicação exige uma pergunta analítica e uma justificativa documentada.

## 9. Normalização e carga

`event_timestamp` foi convertido de texto para `datetime` durante o processamento, preservando o valor original e `raw_line`. O CSV foi carregado em `public.log_events`, no PostgreSQL, usando `TIMESTAMP WITHOUT TIME ZONE`, pois o fuso horário de origem não é conhecido.

A combinação `(source_file, line_number)` identifica uma posição no arquivo para impedir uma segunda carga da mesma linha. O carregador compara o conteúdo existente antes de ignorar uma linha já presente e sinaliza conflitos. Na importação manual inicial, oito linhas (977 a 984) tiveram alterado o prefixo `\\?\GLOBALROOT` de um caminho Windows; elas foram reparadas no banco e verificadas contra o CSV. As consultas de integridade estão em `sql/validation.sql`; a correção pontual está em `sql/repairs/001_restore_unc_path_prefix.sql`.

## 10. Análise exploratória iniciada

### Caminho da investigação

1. Partimos dos 2.000 eventos e contamos as ocorrências de cada `message` completo para identificar textos repetidos. `Warning: Unrecognized packageExtended attribute.` apareceu em 280 eventos. Essa contagem representa ocorrências do texto, não incidentes distintos.
2. Ao examinar os resultados, percebemos que algumas mensagens não são idênticas, mas compartilham um trecho fixo. Selecionamos `Read out cached package applicability for package:` como uma família para investigar essa semelhança sem alterar as mensagens originais.
3. Contamos todos os eventos dessa família e seus textos completos distintos. Depois, verificamos a frequência de cada texto para separar a ideia de família da ideia de repetição exata.
4. A investigação está concentrada, neste momento, em **todas as ocorrências dessa família**. Foram observados formatos de nome de pacote como `Package_for_KB...`, `Microsoft-Windows-...`, `Microsoft-Hyper-V-...` e `Package_for_RollupFix...`; eles ainda não foram classificados nem quantificados como subgrupos.

As consultas reproduzíveis desta etapa estão em [sql/analysis.sql](sql/analysis.sql).

Uma segunda consulta selecionou mensagens que começam com `Read out cached package applicability for package:`. Foram encontradas 558 ocorrências e 280 mensagens completas diferentes. O prefixo define uma família exploratória; os 280 textos diferentes não devem ser interpretados automaticamente como 280 pacotes distintos.

A consulta de frequência, ordenada da maior para a menor contagem, mostrou três mensagens com quatro ocorrências cada e, em seguida, mensagens com duas ocorrências. Combinando essa ordem com os totais da família, a distribuição é: 3 textos aparecem 4 vezes, 269 textos aparecem 2 vezes e 8 textos aparecem 1 vez (`3 × 4 + 269 × 2 + 8 × 1 = 558`). A repetição do texto não demonstra, por si só, duplicação indevida de eventos.

Próximo exame: aprofundar a análise das 558 ocorrências, verificando os formatos de nome de pacote e os estados presentes nas mensagens. A investigação temporal e as demais perguntas definidas para o projeto ficam para depois desta análise.
