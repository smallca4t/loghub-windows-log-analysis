# Ficha de caracterização — Windows_2k.log

## 1. Identificação do dataset

- Arquivo: Windows_2k.log
- Origem declarada: LogHub, disponível no GitHub.
- URL/origem específica: ainda não registrada.
- Formato: .log (texto).
- Tamanho: 285.433 bytes (arquivo local `data/raw/Windows_2k.log`).
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
4. A investigação está concentrada, neste momento, em **todas as ocorrências dessa família**. Os eventos foram classificados provisoriamente pelo início do nome do pacote: `Package_for_KB...`, `Microsoft-Windows-...`, `Microsoft-Hyper-V-...` e `Package_for_RollupFix...`. Mensagens sem correspondência ficariam em `Outros` para revisão.

As consultas reproduzíveis desta etapa estão em [sql/analysis.sql](sql/analysis.sql).

Uma segunda consulta selecionou mensagens que começam com `Read out cached package applicability for package:`. Foram encontradas 558 ocorrências e 280 mensagens completas diferentes. O prefixo define uma família exploratória; os 280 textos diferentes não devem ser interpretados automaticamente como 280 pacotes distintos.

A consulta de frequência, ordenada da maior para a menor contagem, mostrou três mensagens com quatro ocorrências cada e, em seguida, mensagens com duas ocorrências. Combinando essa ordem com os totais da família, a distribuição é: 3 textos aparecem 4 vezes, 269 textos aparecem 2 vezes e 8 textos aparecem 1 vez (`3 × 4 + 269 × 2 + 8 × 1 = 558`). A repetição do texto não demonstra, por si só, duplicação indevida de eventos.

Na tabela abaixo, **eventos** são linhas de log; **mensagens completas diferentes** são os textos distintos dessas linhas. Assim, 541 eventos em `Package_for_KB` contêm 271 textos diferentes, com 270 ocorrências além da primeira de cada texto.

| Grupo provisório pelo prefixo do pacote | Eventos | Mensagens completas diferentes |
| --- | ---: | ---: |
| `Package_for_KB` | 541 | 271 |
| `Microsoft-Hyper-V` | 8 | 4 |
| `Microsoft-Windows` | 8 | 4 |
| `Package_for_RollupFix` | 1 | 1 |
| **Total** | **558** | **280** |

Não houve eventos em `Outros`: os quatro prefixos cobrem a família selecionada neste arquivo. A predominância de `Package_for_KB` descreve esta amostra; a contagem de mensagens distintas não é uma contagem verificada de pacotes únicos.

Os dois valores ao fim da mensagem foram extraídos em todos os 558 eventos da família; não houve linhas em `não extraído`. Os pares abaixo são os **valores registrados**, sem atribuir significado aos códigos numéricos:

| `ApplicableState` | `CurrentState` | Eventos | Mensagens completas diferentes |
| ---: | ---: | ---: | ---: |
| 112 | 112 | 409 | 205 |
| 80 | 112 | 81 | 41 |
| 80 | 0 | 26 | 13 |
| 0 | 0 | 22 | 11 |
| 112 | 0 | 18 | 9 |
| 64 | 0 | 2 | 1 |
| **Total** | | **558** | **280** |

O cruzamento entre subgrupo de pacote e par de valores mostrou:

| Grupo | `ApplicableState` | `CurrentState` | Eventos | Mensagens completas diferentes |
| --- | ---: | ---: | ---: | ---: |
| `Microsoft-Hyper-V` | 112 | 0 | 8 | 4 |
| `Microsoft-Windows` | 112 | 112 | 6 | 3 |
| `Microsoft-Windows` | 112 | 0 | 2 | 1 |
| `Package_for_KB` | 112 | 112 | 402 | 201 |
| `Package_for_KB` | 80 | 112 | 81 | 41 |
| `Package_for_KB` | 80 | 0 | 26 | 13 |
| `Package_for_KB` | 0 | 0 | 22 | 11 |
| `Package_for_KB` | 112 | 0 | 8 | 4 |
| `Package_for_KB` | 64 | 0 | 2 | 1 |
| `Package_for_RollupFix` | 112 | 112 | 1 | 1 |
| **Total** | | | **558** | **280** |

Nesta amostra, `Microsoft-Hyper-V` aparece somente com `(112, 0)`; os pares `(80, 112)`, `(80, 0)`, `(0, 0)` e `(64, 0)` aparecem somente em `Package_for_KB`. Isso descreve a distribuição observada, sem interpretar o significado dos códigos nem uma possível mudança de estado de um pacote.

### Fechamento da família analisada

A extração do identificador completo de pacote e do par de valores cobriu os 558 eventos (`não extraídos = 0`). Foram encontrados **280 identificadores completos de pacote** e **280 mensagens completas diferentes**. A consulta por pacote não encontrou identificadores associados a mais de um par de valores. Portanto, **neste arquivo e com a versão incluída no identificador**, cada pacote distinto corresponde a um único texto completo e a um único par de valores; as demais ocorrências repetem esses textos em outros eventos.

Isso não equivale a contar números de KB únicos sem considerar a versão, nem demonstra que os valores de um pacote nunca mudam fora desta amostra. Os códigos numéricos permanecem sem interpretação semântica nesta análise.

A investigação desta família está concluída. As demais perguntas definidas para o projeto, incluindo a distribuição temporal e as mensagens com `Failed` ou `Warning`, serão analisadas em seguida.
