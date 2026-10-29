# Régua do painel: Nota da obra

Desde 28/10/2026 o painel classifica as obras pela **Nota da obra**: nove itens em sete dimensões (custo, prazo, caixa,
qualidade, segurança, suprimentos e gestão), de 0 a 10, com uma trava de custo e prazo. A proposta, as fontes e a
discussão de cada item estão em `docs/08-criterios-propostos.md` (aprovado pela sessão local em 28/10/2026). A régua
anterior, de oito itens com bônus, saiu do modelo.

**Fonte única.** Faixas, pontos, limites, máximos, nomes e a trava estão no dicionário `NOTA` de
`pbi/scripts/contas_base.py`. Ele gera as medidas `Nota · …`, a tabela `dItemNota` (`pbi/m/dItemNota.m`), as regras que o
Power Query usa para validar a base complementar (`pbi/m/fxRegrasBase.m`), as tabelas calculadas `dRankingNota` e
`dItemRankingNota`, os números do tour e a prévia da nota dos dados fictícios (`pipeline/conferir_ficticios.py`, que é
o oráculo do `conferir_real.py`). Nenhum limite da régua fica escrito à mão em outro lugar. Para mudar uma regra, mude
o dicionário e rode o ciclo (HANDOFF).

## Os nove itens

Quatro itens vêm da planilha **Análise Crítica** da obra (o prazo também usa o **cronograma** da obra); cinco vêm da
**base complementar** (uma planilha por obra, uma aba por mês, modelo BC 2.0).

| # | Dimensão | Item | Fonte | Máximo | Conta (X) | Faixas → pontos |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Custo | Custo (IDC) | Análise Crítica | 3 | IDC = valor agregado ÷ custo aplicado (abaixo) | IDC ≥ 1,00 → 3 · 0,98 → 2,5 · 0,96 → 2 · 0,94 → 1,5 · 0,92 → 1 · 0,90 → 0,5 · abaixo de 0,90 → 0 |
| 2 | Prazo | Atraso em meses | Análise Crítica + cronograma | 2 | meses decorridos − meses agregados (Earned Schedule): o executado de hoje é o previsto de quantos meses atrás | atraso ≤ 0,5 mês → 2 · ≤ 1 → 1,5 · ≤ 2 → 1 · ≤ 3 → 0,5 · mais de 3 → 0. Adiantada leva o ponto cheio. |
| 3 | Prazo | Plano semanal cumprido (PPC) | base complementar | 1 | PPC do mês (média das semanas) | X ≥ 80% → 1 · 70% → 0,5 · 60% → 0,25 · abaixo de 60% → 0 |
| 4 | Caixa | Acerto da previsão de caixa | Análise Crítica | 1 | \|desembolsado no mês ÷ previsto no mês − 1\| | X < 10% → 1 · 10% a 20% → 0,5 · acima de 20% → 0. Conta para mais **e** para menos. |
| 5 | Qualidade | Aprovação na 1.ª inspeção | base complementar | 1 | aprovados na 1.ª inspeção ÷ serviços verificados | X ≥ 95% → 1 · 90% → 0,75 · 85% → 0,5 · 80% → 0,25 · abaixo de 80% → 0 |
| 6 | Segurança | Frequência de acidentes | base complementar | 0,5 | taxa de frequência (NBR 14280) dos últimos 12 meses: acidentes com afastamento × 1.000.000 ÷ HHT | TF = 0 → 0,5 · até 7,5 → 0,25 · acima de 7,5 → 0 |
| 7 | Segurança | Canteiro conforme NR-18 | base complementar | 0,5 | itens conformes ÷ itens aplicáveis do checklist | X ≥ 95% → 0,5 · 85% → 0,25 · abaixo de 85% → 0 |
| 8 | Suprimentos | Entregas no prazo e completas | base complementar | 0,5 | pedidos no prazo e completos ÷ pedidos previstos | X ≥ 90% → 0,5 · 80% → 0,25 · abaixo de 80% → 0 |
| 9 | Gestão | Análise crítica sem pendência | Análise Crítica | 0,5 | checagens da aba que passam, de 3 (abaixo) | 3 de 3 → 0,5 · 2 de 3 → 0,25 · 0 ou 1 → 0 |

As faixas são avaliadas de cima para baixo e vale a primeira que bate; o X é arredondado em 8 casas antes de comparar.

**Custo aplicado e IDC.** Custo aplicado (CA) = desembolsado + contas a pagar + dívida da obra − estoque −
adiantamentos − receita de personalizações. Valor agregado (VA) = crédito do orçamento (executado × orçamento).
IDC = VA ÷ CA; resultado aplicado = VA − CA. A dívida da obra desconta (decisão de 28/10/2026).

**Prazo pelo cronograma.** A curva prevista de cada obra vem da planilha de fluxo financeiro (`fCurvaPrevista`). O
atraso é a distância, em meses, entre hoje e o ponto da curva em que o previsto acumulado iguala o executado de hoje
(interpolado entre os meses). Também saem do cronograma o IDP(t), o término projetado e a folga até a entrega
contratual do cadastro mais os 180 dias de tolerância (art. 43-A da Lei 4.591/64).

**Análise crítica sem pendência.** Três checagens da aba do mês: (1) a conta fecha, o resultado apresentado bate com a
regra da planilha (± R$ 1); (2) há justificativa quando o desembolso do mês foge mais de 10% do previsto; (3) o
previsto acumulado não caiu em relação à aba anterior.

**Valor fora da faixa.** PPC fora de 0 a 100% e aprovados, conformes ou entregues maiores que o total chegam ao modelo
como foram digitados (o Power Query avisa em `fConferencia`), mas o item fica **sem pontos**, e as telas dizem "fora da
faixa", não "falta na base". Texto onde se espera número chega vazio.

**Leitura das bases.** O Power Query (`stgAbasBase`) acha cada campo pelo rótulo da coluna B ("Versão do modelo" é a
âncora) e lê o valor duas colunas à direita (coluna D), em qualquer linha. O mês vem do nome da aba ("SET 2026"); a
obra, do nome do arquivo (`Base complementar - <OBRA>.xlsx`).

- **Mês repetido** (na mesma base ou em duas bases da mesma obra): vale a aba preenchida do arquivo **modificado por
  último**; no mesmo arquivo, a mais à direita. A aba vazia só vale quando nenhuma está preenchida.
- **Aba vazia conta como sem base:** a obra fica pendente no mês.

Na entrega os arquivos vão embutidos no modelo; a pasta do computador só entra no perfil local do gerador (HANDOFF,
"Fonte de dados").

## Nota, trava, status e pendente

- **Nota da obra** = soma dos pontos dos nove itens, **só com os nove itens com dado**. Vai de 0 a 10; não há bônus.
- **Status pela nota:** **estável** com nota 8 ou mais · **atenção** de 6 a 7,99 · **crítico** abaixo de 6.
- **Trava:** IDC abaixo de 0,90 **ou** atraso acima de 3 meses deixa a obra **crítica com qualquer nota**. As telas
  dizem o motivo (`Nota · trava · motivo`).
- **Pendente** (4º estado, tracejado nas telas): falta algum item, na base ou na planilha. A obra mostra os pontos que
  já dá para calcular ("X de Y possíveis"), mas fica **sem nota e sem status**. Não há nota inventada.
  - As telas dizem de onde vem a falta: "faltam 2 itens na base", "falta 1 item na planilha". O valor fora da faixa vem
    à parte: "1 item fora da faixa" ou, com falta junto, "faltam 3 · 1 fora".
- **Obra sem aba da Análise Crítica no mês não aparece**, mesmo com a base complementar preenchida: a base sozinha não
  põe a obra no painel.

## Ordem, obra em foco e "onde perde pontos"

- **Pontos perdidos** de uma obra = máximo dos itens com dado − pontos obtidos. A obra pendente também perde pontos
  nos itens que já têm dado.
- **Ordem das obras** (lista da T1, gaveta, T4): mais pontos perdidos primeiro; empate pela menor nota (a pendente vai
  depois das que têm nota); depois o nome.
- **Obra em foco** (T2 e T3): a escolhida no seletor ou, na linha "Mais crítica do mês", a primeira dessa ordem no mês
  de referência.
- **Onde a carteira perde pontos** (T1): os pontos perdidos somados por item (ou por dimensão), pelas obras do recorte.
- **Empates.** Quando itens empatam no topo dos pontos perdidos, as frases citam todos ("no custo e no prazo"). Com um
  topo único, citam também o segundo se ele for único; se o segundo empata, só o topo.
- **Carteira** (contagens por status e na trava): de **um mês** (eixo do mês ou mês de referência); com mais de um mês
  no contexto, vazia. Só obras com aba da Análise Crítica no mês.

## Entrou, saiu e abriu em crítico

Só contam entre meses com **nota completa**:

- **entrou** em crítico: crítica no mês e com nota completa abaixo de crítico no mês anterior;
- **saiu** de crítico: crítica no mês anterior e com nota completa abaixo de crítico no mês;
- **abriu** em crítico: a **primeira nota completa** da obra já veio crítica (antes, só meses pendentes ou sem
  planilha). Conta à parte, não como entrada.
- Passar de pendente para crítico não é "entrar". Crítico → pendente → crítico não entra nem abre.

## Comparações com o mês anterior

- **Mês anterior de uma obra = a aba anterior da mesma planilha** (colunas `*Anterior` de `fAnaliseCritica`). Obra
  que abre a planilha não tem mês anterior: variação vazia.
- **Variação da carteira** (R$ e p.p.) compara **só as obras que têm aba no mês e no mês anterior**. Obra que entra não
  vira "ganho" nem "perda" da carteira.
- **Justificativa do desembolso:** exigida quando o desvio do mês passa de ±10% (regra da Análise Crítica; também é a
  checagem 2 do item 9).
- **Resultado sem estoque e adiantamentos** e **variação do resultado** seguem como informação (cartões, T2, T4).

## Perguntas que cada parte do painel responde (para o storytelling)

1. **Quais obras e itens da nota pedem atenção neste mês, e por quê?** → nota, status, trava e os itens que mais perdem
   pontos (T1).
2. **O resultado é de verdade?** → resultado aplicado, IDC e resultado sem estoque e adiantamentos (T2).
3. **Está no ritmo?** → curva prevista × executado, atraso em meses e término projetado (T3).
4. **Está piorando? Gastou fora do previsto no mês e justificou?** → resultado mês a mês, desembolso × previsto e
   justificativa (T4).
5. **O canteiro está seguro, faz certo da primeira vez e recebe material no prazo?** → meses sem acidente com
   afastamento, taxa de frequência de 12 meses contra a média do setor, NR-18, 1.ª inspeção, entregas no prazo e chuva ×
   executado no mês (T5; o PPC fica na T3).
6. **Posso confiar no número?** → avisos de qualidade da planilha e da base (`fConferencia`).

## Indicadores por obra × mês (fora da régua, calculados no painel)

| Indicador | Conta | Leitura |
|---|---|---|
| Orçamento projetado | da aba | Base de todas as porcentagens |
| % previsto / executado do mês | da aba | Ritmo do mês (no tooltip do mês da curva S e do PPC, T3) |
| % previsto / executado acumulado | da aba | Avanço físico |
| Desvio físico acumulado | (executado acum. − previsto acum.) × 100, em p.p. | < 0 = atrasada |
| Crédito do orçamento (VA) | executado acum. × orçamento | Quanto podia ter gasto |
| Resultado da obra | conta do quadradinho da aba | Ganho (+) ou perda (−) econômica acumulada |
| Resultado % do orçamento | resultado ÷ orçamento | Comparável entre obras |
| Variação do resultado no mês | resultado % − resultado % do mês anterior, em p.p. | Tendência |
| Ativos não consumidos | saldo de contrato + adiantamentos + estoque + equipamentos | Pago e ainda não virou obra |
| Resultado sem ativos | resultado − ativos não consumidos | Quanto o resultado depende de estoque/adiantamento |
| Desvio do desembolso do mês | desembolsado do mês ÷ previsto do mês − 1 | Gasto fora do planejado |
| Término projetado | início + duração prevista ÷ IDP(t) (Lipke, IEAC(t)) | Quando a obra deve terminar no ritmo de hoje |
| Onde cai o término projetado | até a entrega contratual · nos 180 dias de tolerância · depois deles | Cartão e linha do tempo da T3 (Lei 4.591/64, art. 43-A) |
| Taxa de gravidade (12 meses) | dias perdidos × 1.000.000 ÷ HHT | Só informação (NBR 14280) |
| Dias impraticáveis por chuva | da base | Contexto do prazo (quadra chuvosa de Natal) |
| Meses sem acidente com afastamento | meses seguidos, até o de referência, depois do último mês com acidente em alguma obra do recorte | Cartão escuro da T5 (a base é mensal: não dá o dia) |
| Taxa de frequência da carteira (12 meses) | acidentes 12 meses ÷ HHT 12 meses × 1.000.000, obras somadas | Cartão da T5, contra a média do setor (7,5) |
| Mês de chuva | 5 ou mais dias impraticáveis por obra, em média (`T5 · Chuva · limite de mês chuvoso`) | Leitura de Chuva e ritmo: executado médio nos meses de chuva × nos outros |

---

## Histórico

- **04/10/2026:** primeira régua da Vizu (pontos de 0 a 100 por cinco indicadores, com pesos e "em mobilização").
- **13/10/2026:** trocada por uma régua de oito itens com bônus, lida de uma base complementar 1.0.
- **28/10/2026:** trocada pela **Nota da obra** (docs/08), com a base complementar 2.0 e o cronograma da obra.
