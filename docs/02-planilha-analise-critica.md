# As planilhas de origem · estrutura, conta e leitura

Tudo em `dados/` é **fictício**: uma construtora inventada de Natal/RN com sete empreendimentos. Quem gera é
`pipeline/gerar_ficticios.py`; quem confere é `pipeline/conferir_ficticios.py` (gabarito em `dados/_gabarito/`).
O Power Query lê as planilhas **pelo rótulo**, nunca pelo endereço (`pbi/m/fxLerAba.m`, `stgAbasADO.m`, `stgCrono.m`).

| Pasta | O que tem | Quem lê |
|---|---|---|
| `dados/cadastro/obras_cadastro.csv` | uma linha por obra: código, SPE, nome na cronograma, pasta da Análise Crítica, bairro, unidades e **entrega contratual** | `stgCadastro.m` |
| `dados/analise-critica/<OBRA>/Analise Critica <OBRA>.xlsx` | uma aba por mês, de SET25 a SET26 (a TIROL começa em FEV26) | `stgAbas.m` → `fxLerAba.m` |
| `dados/bases-complementares/Base complementar - <OBRA>.xlsx` | modelo BC 2.0, uma aba por mês (OUT 2024 a SET 2026) | `stgAbasADO.m` |
| `dados/cronograma/PLANILHA DE FLUXO FINANCEIRO ATUALIZADO EM 092026.xlsx` | PREVXREA de set/26 e a curva prevista (linha de base) de cada obra | `stgCrono.m` |

## As obras

| Obra | Bairro | Início | Término previsto | Entrega contratual | Papel no roteiro |
|---|---|---|---|---|---|
| CAJUEIRO | Candelária | out/23 | dez/26 | fev/27 | terminando (97% em set/26), estável |
| PONTA NEGRA | Ponta Negra | nov/24 | abr/27 | jun/27 | estável, obra de alto padrão |
| DUNAS | Capim Macio | mar/25 | jun/27 | ago/27 | **melhora**: atenção até fev/26, estável de mar/26 em diante |
| POTENGI | Potengi | fev/25 | jun/27 | ago/27 | **crítico por prazo**: chuva na estrutura e entrega de material fraca; 3,6 meses de atraso em set/26 |
| REDINHA | Redinha | ago/24 | mar/27 | mai/27 | **crítico por custo**: IDC cai de 0,97 para 0,89 |
| JANGADA | Areia Preta | jun/25 | jan/28 | mar/28 | atenção o ano todo |
| TIROL | Tirol | fev/26 | nov/28 | jan/29 | **começando**: fundação na quadra chuvosa |

A quadra chuvosa de Natal (março a julho, pico em abril) entra como dias impraticáveis por chuva na base e como atraso
no físico, maior nas fases de fundação e estrutura. Clientes (personalizações por unidade), títulos e notas fiscais
são inventados.

## Análise Crítica (versão 01)

Título interno: **ANÁLISE DE DESEMPENHO ECONÔMICO DA OBRA**. Uma aba por mês com nome MMMAA (OUT25, …, SET26) e uma aba
LEIA-ME. Todas as abas têm o mesmo layout.

**Entradas** (rótulo na coluna B):

| Passo | Campo | Célula |
|---|---|---|
| 1 | Projeto (obra) | D24 |
| 2 | Mês de análise | E26 |
| 3 | Orçamento da obra projetado (com INCC no a realizar) · tipo do orçamento | J28 · J29 |
| 4 a 7 | % previsto e executado do mês; previsto e executado acumulados | F31 · F33 · F35 · F37 |
| 8 | Crédito do orçamento = F37 × J28 | F39 |
| 8 a 14 | Saldo de contrato, adiantamentos, estoque, equipamentos, personalizações, contas a pagar (totais das tabelas) | F41 a F53 |
| 15 | Valor desembolsado pela obra · corrigido (sem os itens irregulares) | F55 · F56 |
| 16 | Dívida da obra a ser paga | F58 |

**Tabelas anexadas** (descrição em B ou G, valor três colunas à direita, total com `SUM` na linha "Total"): saldo de
contrato (B63), adiantamento de materiais não estocados (G63), adiantamento de serviços não medidos (B77), estoque de
materiais (G77), equipamentos comprados (B91), receitas de personalizações (G91), contas a pagar dos medidos (B105),
itens apontados irregularmente no relatório (G105) e dívida da obra a ser paga (B118).

**Bloco de resultado** (âncora "RESULTADO PARA UTILIZAR NA APRESENTAÇÃO", B132; área de impressão A132:J157): itens 01 a
10 em C145:E154 e

- **Resultado mensal da obra** (D155) = itens 1 a 7 − contas a pagar − desembolsado corrigido − **dívida da obra**.
  Na versão 01 a dívida (material de outra obra da carteira usado nesta) **desconta**: é custo desta obra (docs/08, L13).
- Resultado do mês anterior (D156) = D155 da aba anterior.
- Tabela informativa do desembolso do mês (G135:J140): previsto (J136), desembolsado (J137), diferença (J138) e a
  justificativa (G140), obrigatória quando a diferença passa de 10%.

**Significado de cada item** (B160 em diante): rótulo terminado em ":" e o texto na linha de baixo; o painel usa nos
tooltips (`dItem`).

**Falhas de preenchimento de propósito** (para o item "análise crítica sem pendência" e o `fConferencia`):
REDINHA mai/26 com o resultado digitado por cima da fórmula; JANGADA mar/26 com o previsto acumulado digitado abaixo do
mês anterior; DUNAS nov/25 e POTENGI jun/26 sem justificativa com o caixa desviando mais de 10%; TIROL abr/26 com o mês
de análise desatualizado. A JANGADA troca o orçamento preliminar pelo executivo em abr/26.

## Base complementar 2.0

Âncora "Versão do modelo" (B4, valor `BC 2.0` em D4); cada campo tem o rótulo na coluna B e o valor duas colunas à
direita (D). Rótulos, versão e faixas válidas vêm do dicionário `NOTA` de `pbi/scripts/contas_base.py`.

| Seção | Campo | Uso na nota |
|---|---|---|
| — | Obra · Gestor da obra | identificação |
| Planejamento | PPC do mês (fração) | plano semanal cumprido |
| Qualidade | Serviços verificados · Aprovados na primeira inspeção | aprovação na 1.ª inspeção |
| Segurança | Horas-homem trabalhadas (HHT) · Acidentes com afastamento · Dias perdidos | taxa de frequência em 12 meses (NBR 14280) |
| Segurança | Itens NR-18 aplicáveis · Itens NR-18 conformes | canteiro conforme NR-18 |
| Suprimentos | Pedidos com entrega prevista · Pedidos entregues no prazo e completos | entregas no prazo |
| Clima | Dias impraticáveis por chuva | informação (T5) |

## Cronograma

- **PREVXREA SET 26**: cabeçalho na linha 5 (OBRA, TIPO DE ORÇAMENTO, M2 EQUIVALENTE (NBR), ORÇ OBRA RESULTADO, REALIZADO
  ACUMULADO, PREVISTO, DESVIO) e, depois de DESVIO, o previsto dos meses seguintes, com as datas na linha 6. O término
  previsto é o último mês com previsto.
- **FLUXO-FINACEIRO <estágio> <OBRA>**: a curva prevista (linha de base) do início ao término: mês (B), % previsto no
  mês (C), % previsto acumulado (D) e custo previsto (E). A soma da coluna E fecha no orçamento. É a curva do atraso em
  meses (cronograma agregado) e bate com o previsto acumulado das abas da Análise Crítica.
