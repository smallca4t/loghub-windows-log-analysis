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

## 7. Próxima etapa

Validar a qualidade dos campos extraídos antes de normalizar ou persistir dados: frequências de level e component, mensagens vazias, intervalo temporal, validade real dos timestamps e ocorrência de linhas idênticas repetidas. Registros repetidos não devem ser removidos sem justificativa baseada no contexto do log.

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

As repetições exatas não serão removidas nesta etapa: podem representar ocorrências legítimas do processo registrado. A deduplicação só poderá ser considerada posteriormente se houver uma pergunta analítica e uma justificativa documentada.

## 9. Próxima etapa revisada

Com a validação concluída, a próxima atividade é definir normalizações necessárias e seguras. O ponto de partida será converter `event_timestamp` de texto para datetime, preservando `raw_line` e os valores originais para rastreabilidade.