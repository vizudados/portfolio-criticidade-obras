# Critérios propostos · F1 (para aprovação)

Proposta da sessão na nuvem, 28/10/2026. **Nada mudou no modelo, no DAX, no M, nos dados nem nas telas**: isto é o
que a F2 e a F3 aplicam depois do aval. Fontes numeradas entre colchetes, lista na §9.

## 1. Recomendação em cinco linhas

1. Trocar a régua do ADO por uma **Nota da obra** de 0 a 10, **sem bônus**, com **9 itens objetivos** em 7 dimensões:
   custo, prazo, caixa, qualidade, segurança, suprimentos e gestão.
2. **Custo pelo IDC** (valor agregado ÷ custo do que já virou obra) e **prazo em meses de atraso** (cronograma
   agregado, de Lipke). Os dois respondem às perguntas que hoje ficam fora da nota.
3. Saem as opiniões (6 termômetros, assertividade Alto/Médio/Baixo) e o ponto extra. Entram números de canteiro com
   fonte pública: PPC, aprovação na 1.ª inspeção, taxa de frequência de acidentes, NR-18 e entregas no prazo.
4. Uma faixa só por item, com degraus iguais e sem penhasco, e uma **trava**: custo ou prazo zerado → crítico.
5. Telas mais enxutas (T1 a T4) e uma **tela nova, T5 · Canteiro**, que usa os dados completos da F2.

## 2. Lacunas da régua atual

| # | Lacuna | Onde | Efeito |
|---|---|---|---|
| L1 | O item Orçamento usa o resultado da planilha (D155), que conta como ganho o **saldo de contrato** (desconto que ainda não aconteceu, "artifício temporário" no texto da própria planilha) e os **equipamentos a valor de mercado**. Os dois são declarados pela obra. | `contas_base.py` (ADO · orcamento) | Um desconto futuro e uma revenda estimada sobem a nota hoje. A pergunta "o resultado é de verdade?" fica fora da régua. |
| L2 | **Três tabelas de faixa** pelo tipo do orçamento e **penhasco** no fim (−5% → de 3,25 para 0; −3% → de 3 para 0). | `ADO["orcamento"]` | 45% da nota some num degrau. Tipo não reconhecido = item sem dado. |
| L3 | **Prazo pesa 5%** e é sim/não (atraso ≤ 3,5 p.p.). O desvio em p.p. não diz quanto tempo falta e tende a zero no fim da obra, mesmo atrasada [3]. Não há término projetado nem ligação com a entrega contratual. | `ADO["fisico_financeiro"]` | Uma obra meses atrasada perde no máximo 0,5. |
| L4 | **Médio Prazo + PPC**: a PPC zera quando o Médio Prazo passa de 100%, com teto de 2 para o par. | `ADO["medio_prazo"]`, `teto_prazo` | Difícil de explicar na tela. Os dois % são digitados, sem definição no painel. |
| L5 | **Fluxo de caixa** pune gastar menos igual a gastar mais, mas as telas não pintam o desvio negativo de vermelho (decisão de 07/10). | `ADO["fluxo_caixa"]`, T1/T4 | A nota e a cor dizem coisas diferentes, e o nome não diz que se mede o **acerto da previsão**. |
| L6 | **Termômetros**: seis notas de opinião (0 a 10), pesos que somam 1,5, depois ÷ 10. "Proteção" e "Projeção da marca" não têm definição. A conta precisou ser corrigida em 20/10. | `ADO["termometros"]` | Ninguém consegue dizer o que fazer para subir a nota. |
| L7 | **Segurança** só como opinião: sem taxa de frequência (NBR 14280) nem conformidade NR-18. | — | O risco mais grave de canteiro não tem número. |
| L8 | **Qualidade e retrabalho** só como opinião. | — | Retrabalho chega a 12% do custo da obra [9] e não aparece. |
| L9 | **Suprimentos** só como opinião. | — | Atraso de material só aparece depois, no físico. |
| L10 | **Assertividade da análise crítica** é opinião. As checagens que o Power Query já faz (conta que não fecha, previsto que cai, justificativa em branco) não entram. | `ADO["assertividade_ac"]`, `fConferencia` | A pergunta 5 do painel ("posso confiar no número?") fica fora da nota. |
| L11 | **Ponto extra** discricionário: a nota passa de 10. | `ADO["ponto_extra"]` | Escala sem teto; o bônus não tem critério. |
| L12 | **Nota compensatória**: com o Orçamento zerado, a obra ainda chega a 6 (5,5 + bônus) e fica em atenção. | `ADO["status"]` | Uma obra com resultado de −6% do orçamento pode não ser crítica. |
| L13 | **Dívida da obra soma** ao resultado (item 10 da planilha): um custo que a obra deve aumenta o resultado. | docs/02, `Resultado da obra` | Sinal invertido. Os dados são nossos agora, então dá para corrigir. |

## 3. Régua nova: Nota da obra

### 3.1 Itens, pesos e faixas

O X é calculado por obra e por mês. As faixas são lidas de cima para baixo e vale a primeira que bate. Soma máxima: 10.

| # | Dimensão · item | Peso | X (conta) | Faixas → pontos |
|---|---|---|---|---|
| 1 | **Custo · IDC** | 3,0 | VA ÷ CA. VA (valor agregado) = executado acumulado × orçamento. CA (custo aplicado) = desembolsado + contas a pagar + dívida − estoque − adiantamentos (materiais e serviços) − receita de personalizações. | X ≥ 1,00 → 3 · 0,98 ≤ X < 1,00 → 2,5 · 0,96–0,98 → 2 · 0,94–0,96 → 1,5 · 0,92–0,94 → 1 · 0,90–0,92 → 0,5 · X < 0,90 → 0 |
| 2 | **Prazo · atraso em meses** | 2,0 | X = meses decorridos − meses agregados. Meses agregados = ponto da curva prevista em que o previsto acumulado iguala o executado acumulado de hoje (interpolação entre meses) [3]. | X ≤ 0,5 → 2 · ≤ 1 → 1,5 · ≤ 2 → 1 · ≤ 3 → 0,5 · > 3 → 0 |
| 3 | **Prazo · plano semanal cumprido (PPC)** | 1,0 | Pacotes concluídos ÷ pacotes planejados nas semanas do mês [4]. | X ≥ 80% → 1 · 70–80% → 0,5 · 60–70% → 0,25 · < 60% → 0 |
| 4 | **Caixa · acerto da previsão** | 1,0 | \|desembolsado no mês ÷ previsto no mês − 1\| (a conta de hoje). | X < 10% → 1 · 10–20% → 0,5 · > 20% → 0 |
| 5 | **Qualidade · aprovação na 1.ª inspeção** | 1,0 | Serviços aprovados na primeira verificação (FVS) ÷ serviços verificados no mês [6]. | X ≥ 95% → 1 · 90–95% → 0,75 · 85–90% → 0,5 · 80–85% → 0,25 · < 80% → 0 |
| 6 | **Segurança · frequência de acidentes** | 0,5 | TF = acidentes com afastamento × 1.000.000 ÷ HHT, nos **últimos 12 meses** [7]. | X = 0 → 0,5 · 0 < X ≤ 7,5 → 0,25 · X > 7,5 → 0 |
| 7 | **Segurança · canteiro conforme NR-18** | 0,5 | Itens "sim" ÷ itens aplicáveis do checklist NR-18 do mês [8]. | X ≥ 95% → 0,5 · 85–95% → 0,25 · < 85% → 0 |
| 8 | **Suprimentos · entregas no prazo e completas** | 0,5 | Pedidos entregues no prazo e completos ÷ pedidos com entrega prevista no mês [6]. | X ≥ 90% → 0,5 · 80–90% → 0,25 · < 80% → 0 |
| 9 | **Gestão · análise crítica sem pendência** | 0,5 | Quantas das 3 checagens a aba do mês passa: a conta fecha (resultado = regra, ± R$ 1); há justificativa quando o caixa desvia mais de 10%; o previsto acumulado não caiu. | 3 → 0,5 · 2 → 0,25 · 0 ou 1 → 0 |

**Status:** estável com 8 ou mais · atenção de 6 a 7,99 · crítico abaixo de 6 (os limites de hoje).
**Trava:** IDC abaixo de 0,90 **ou** atraso acima de 3 meses → crítico, qualquer que seja a nota.
**Pendente:** continua (sem nota quando falta item). Com os dados completos da F2, só aparece se a gente quiser
mostrar o estado.

A régua continua com **fonte única** no dicionário de `pbi/scripts/contas_base.py`, que gera DAX, `dItem…`, regras
do M e oráculo, como hoje.

### 3.2 De onde vem o dado e por que entra

| # | Dado (F2) | Critério público | Por que entra · como a tela explica |
|---|---|---|---|
| 1 | Análise Crítica: F37 (executado acumulado), J28, F55/F56, tabelas anexadas. **Nenhum campo novo.** | Gerenciamento do valor agregado: IDC = VA ÷ CR [1][2]. | Responde "o resultado é de verdade?" (L1). Estoque e adiantamentos saem do custo porque ainda não viraram obra (é a regra do valor agregado). Desconto de contrato e revenda de equipamento não contam porque ainda não aconteceram. **VA − CA = resultado aplicado** = resultado da planilha sem o saldo de contrato e os equipamentos, com a dívida descontando. Uma escala só para todo tipo de orçamento (L2), meio ponto a cada 2 centésimos. *"Para cada R$ 1,00 aplicado, a obra entregou R$ 0,97 de orçamento."* |
| 2 | Curva prevista mês a mês da obra (linha de base da cronograma) e executado acumulado. | Earned Schedule, Lipke: ES, SPI(t) = ES ÷ AT e término projetado [3]; tolerância legal de 180 dias para a entrega (art. 43-A da Lei 4.591/64) [10]. | Prazo em meses é a unidade que a diretoria usa (L3). Não converge no fim da obra. O limite de 3 meses é metade da tolerância legal. *"Em agosto a obra fez o que o cronograma previa para junho: 2 meses de atraso."* |
| 3 | Base complementar: PPC do mês (o campo já existe). | Last Planner System: PPC [4]. Base com 133 obras brasileiras [5]. | Indicador **antecedente** do atraso. Substitui o par Médio Prazo + PPC e a regra que zera (L4). *"De cada 10 tarefas prometidas na semana, 7 foram feitas."* |
| 4 | Análise Crítica: J136 e J137 (sem mudança). | Regra interna da planilha (justificativa acima de ±10%). Não achei critério público melhor. | Fica, com nome novo: a tesouraria precisa acertar a previsão nos dois sentidos. Assim a régua não contradiz a cor das telas (L5). |
| 5 | Base complementar: serviços verificados e aprovados na 1.ª inspeção (FVS). | PBQP-H/SiAC: inspeção dos serviços controlados [6]. Retrabalho de 1% a 12% do custo [9]. | Mede o retrabalho (L8), no lugar do termômetro de Qualidade. *"92% dos serviços passaram na primeira inspeção."* |
| 6 | Base complementar: HHT do mês e acidentes com afastamento (e dias perdidos, para informação). | NBR 14280: taxa de frequência por milhão de HHT [7]. Setor: 14,98 acidentes por mil vínculos/ano em 2018 [11], ≈ 7,5 por milhão de HHT com 2.000 h/ano por vínculo (conversão nossa). | Segurança com número (L7). Janela de 12 meses porque em obra pequena um acidente num mês dá TF acima de 20. Zero acidente vale o ponto cheio; até a média do setor, metade. |
| 7 | Base complementar: itens aplicáveis e itens conformes do checklist NR-18. | Manual de SST da CBIC (2021), Anexo A: 7 checklists da NR-18 [8]. | Indicador **antecedente** da segurança: mede o canteiro antes do acidente. |
| 8 | Base complementar: pedidos previstos no mês e pedidos entregues no prazo e completos. | PBQP-H/SiAC: aquisição e avaliação de fornecedores [6]. A conta "no prazo e completo" é nossa. | Suprimentos com número (L9). Explica atraso antes de ele chegar ao físico. |
| 9 | Análise Crítica (colunas que o M já lê: `Resultado`, `ResultadoRegra`, `Justificativa`, `PrevAcum`, `PrevAcumAnterior`). **Nenhum campo novo.** | Regra interna. São as checagens de `fConferencia`. | Põe "posso confiar no número?" dentro da nota (L10), sem opinião. |

**Saem:** Médio Prazo, Assertividade da AC, os seis termômetros (Engenharia, Qualidade, Suprimentos, Segurança,
Proteção e Projeção da marca), o ponto extra e a área do ponto extra (L4, L6, L10, L11).

**Fica fora da nota (e por quê):** indicadores de sustentabilidade do PBQP-H (resíduo, água e energia por trabalhador
e por m²) não têm valor de referência público [12]. A taxa de gravidade oscila demais em obra pequena; aparece só no
tooltip da T5. O CUB/m² do Sinduscon-RN (NBR 12721) compara orçamento, não desempenho mensal.

## 4. Nomes: atual → novo

| Atual | Novo | Por quê |
|---|---|---|
| ADO · Nota Final do ADO | **Nota da obra** | "ADO" é a sigla do formulário de origem e o leitor do portfólio não a conhece. |
| prefixo `ADO · …`, `dItemADO`, `fADO`, `fxRegrasADO`, `pPastaBasesADO` | `Nota · …`, `dItemNota`, `fBaseObra`, `fxRegrasNota`, `pPastaBases` | O mesmo nome na tela e no código (pergunta 2 da §8). |
| Base complementar do ADO (modelo ADO-BC 1.0) | Base complementar da obra (modelo 2.0) | Layout novo (§7). |
| Orçamento (item) | **Custo · IDC** | Diz o que mede. |
| Físico-Financeiro (item) | **Prazo · atraso em meses** | Unidade de tempo. |
| Médio Prazo · Média PPC | sai · **Plano semanal cumprido (PPC)** | Fica um, sem a regra que zera. |
| Fluxo de caixa (item) | **Acerto da previsão de caixa** | Explica por que gastar menos também tira ponto. |
| Assertividade da análise crítica | **Análise crítica sem pendência** | Checagem objetiva, não opinião. |
| Termômetros | **Aprovação na 1.ª inspeção · Frequência de acidentes · Canteiro conforme NR-18 · Entregas no prazo e completas** | Um número com fonte em cada um. |
| Ponto extra (bônus) | sai | — |
| Crédito do orçamento | **Valor agregado (VA)** | Termo público [1]; tooltip: "quanto a obra podia ter gasto pelo que executou". |
| (não existe) | **Custo aplicado (CA)** | Desembolsado e a pagar, menos o que ainda não virou obra. |
| Ativos não consumidos (saldo + adiantamentos + estoque + equipamentos) | **Pago e não aplicado** (estoque + adiantamentos) · **A realizar** (saldo de contrato + equipamentos) | Separa o que já foi pago e está guardado do que ainda é promessa. |
| Resultado sem estoque e adiantamentos (`Resultado sem ativos` no código) | **Resultado aplicado** (VA − CA) | Um número só no lugar de dois (o da planilha continua como referência); o mesmo nome na tela e no código. |
| O quadradinho | **Composição do resultado** | O apelido não diz nada a quem vê de fora. |
| Desvio do desembolso no mês · Justificativa do desembolso | **Desvio de caixa do mês · Justificativa do desvio de caixa** | Liga ao item 4. |
| Itens do ADO (T2) · Onde a carteira perde pontos (T1) | **Itens da nota** · Onde a carteira perde pontos (por dimensão) | — |
| Como os meses evoluíram (T1) | **Status das obras mês a mês** | Diz o que o gráfico mostra (§5). |

## 5. Telas: o que resumir e por quê

**T1 · Visão geral** (quais obras pedem atenção e por quê?)
- Cartões: cada um fica com **um número por dimensão**: Obras por status · Custo (IDC da carteira e resultado
  aplicado) · Prazo (atraso médio ponderado, em meses) · Caixa (desvio do mês) · Canteiro (TF 12 meses e 1.ª
  inspeção). Hoje o Físico mostra três números da mesma conta e o Sem estoque repete o Resultado.
- Lista de obras: o texto "os dois itens em que mais perde" vira **7 quadradinhos por dimensão**, pintados pela fração
  dos pontos obtidos. Lê-se de relance, na mesma ordem em todas as linhas.
- Onde a carteira perde pontos: de 8 itens para **7 dimensões**. Cabe no painel de 338 px com a fonte v2; o item vai
  para o tooltip.
- Como os meses evoluíram: a contagem empilhada vira **mapa obra × mês** (7 × 12 células de 32 × 30 no mesmo painel).
  A contagem esconde quem mudou de status; com os dados completos, toda célula tem valor.

**T2 · Análise crítica** (por que a obra tem essa nota?)
- O quadradinho (10 linhas e entradas, 548 × 584) e a cascata mostram a mesma conta duas vezes. **Fica a cascata**:
  VA → custo aplicado → resultado aplicado → + a realizar (saldo de contrato e equipamentos) → resultado da planilha.
  As 10 linhas vão para o tooltip do degrau, que já lista as linhas anexadas.
- "Com e sem estoque" (texto) e o cartão "Mês anterior" saem: um repete o cartão de resultado e o outro, o mês a mês.
- **Itens da nota** ganha o espaço do quadradinho: 9 linhas com X, faixa, pontos e uma minissérie de 12 meses.
- Mês a mês: as duas séries (resultado e sem estoque) viram **IDC mês a mês**, com linha em 1,00 e em 0,90. Uma série
  só, na mesma escala para todas as obras; os valores em R$ ficam no tooltip.
- Desembolso do mês: fica.

**T3 · Avanço físico** (a obra está no ritmo?)
- Cartões: Desvio, Executado e Previsto são a mesma conta. Ficam **Atraso (meses)** · No mês · **PPC do mês** ·
  **Término projetado**, com a entrega contratual e os 180 dias no contexto.
- Ritmo do mês (previsto × executado em cada mês) é a derivada da curva S e já está no tooltip do mês da curva. Sai.
  No lugar entra **PPC mês a mês**, com linha em 80%: o sinal que chega antes do atraso.
- Avanço das obras: a barra passa a ser pintada pelo item de prazo e o rótulo vira meses de atraso.
- Linha do tempo: ganha a **marca do término projetado** e a faixa de 180 dias depois da entrega contratual.

**T4 · Resultado no tempo** (está piorando? o caixa bateu?)
- O cartão "Mês anterior" sai: repete a coluna anterior do gráfico.
- Resultado da carteira mês a mês: **uma série** (resultado aplicado), com o resultado da planilha como traço sobre a
  coluna (a distância entre os dois é o que ainda está a realizar). Duas barras lado a lado em 12 meses ficam finas
  demais.
- Resultado por obra e Desembolso por obra (duas tabelas com as mesmas obras) viram **uma tabela**: obra · IDC ·
  variação no mês · desvio de caixa · justificativa. Os dois gráficos de colunas ganham a altura que sobra.

Tooltips, leituras, versos e textos do tour acompanham cada troca na F3.

## 6. Tela nova: T5 · Canteiro

**Pergunta:** o canteiro está seguro, fazendo certo da primeira vez e recebendo material no prazo?

- **Cartões:** dias sem acidente com afastamento · TF 12 meses (com a média do setor) · conformidade NR-18 ·
  aprovação na 1.ª inspeção · entregas no prazo.
- **Segurança por obra:** barra da TF 12 meses com linha em 7,5 (setor) e ponto da conformidade NR-18.
- **Qualidade mês a mês:** 1.ª inspeção por obra (linhas finas, a obra em foco em preto), meta de 95%.
- **Suprimentos por obra:** entregas no prazo e completas, com meta de 90%.
- **Chuva e ritmo:** dias impraticáveis por chuva × executado no mês da carteira. Mostra a quadra chuvosa de Natal (de
  março a julho, com pico em abril; normal do INMET para abril de 240,5 mm [13]), que a F2 vai imprimir no físico.

Ela usa só dados que a F2 já vai gerar (§7). Se a T5 entrar no tour, **a Lia precisa de uma pose a mais**, feita na
sessão local.

## 7. O que muda nos dados (para a F2)

- **Base complementar 2.0** (uma por obra, uma aba por mês, mesma leitura por rótulo): Gestor · PPC · Serviços
  verificados · Aprovados na 1.ª inspeção · HHT · Acidentes com afastamento · Dias perdidos · Itens NR-18 aplicáveis ·
  Itens NR-18 conformes · Pedidos previstos · Pedidos no prazo e completos · Dias impraticáveis por chuva.
- **Cadastro:** data de entrega contratual.
- **Cronograma:** curva prevista mês a mês de cada obra (linha de base). Na falta dela, o previsto acumulado das abas
  da Análise Crítica serve de curva.
- **Análise Crítica:** mesmo layout. Só muda o sinal da dívida no resultado, que passa a descontar (L13). É a
  "coisinha diferente" que o Alisson pediu.
- Os sete empreendimentos ficam como estão no HANDOFF.

## 8. Decisões para o Alisson

1. Aprova a régua da §3 (9 itens, pesos, faixas e a trava)?
2. Troca "ADO" por "Nota da obra" também no código (medidas e tabelas)? Recomendo que sim.
3. Faz a T5 · Canteiro? Se ela entrar no tour, precisa de uma pose nova da Lia.
4. A dívida da obra passa a descontar no resultado fictício (L13)?

## 9. Fontes

Consultadas por busca na web em 28/10/2026. A rede da sessão bloqueou a abertura das páginas, então as citações vêm
dos resumos da busca. Vale abrir as que forem para o texto público.

1. PMI, *PMBOK Guide*, 6.ª ed., processo Controlar os Custos (7.4), análise de valor agregado: IDC = VA ÷ CR,
   IDP = VA ÷ VP. Resumo em português: Sienge, "Índice de desempenho de custos",
   https://sienge.com.br/blog/indice-de-desempenho-de-custos/
2. Aplicação em obras: Sienge, "Análise de valor agregado", https://sienge.com.br/blog/analise-de-valor-agregado/;
   Boletim do Gerenciamento (NPPG/UFRJ), https://nppg.org.br/revistas/boletimdogerenciamento/article/download/28/24
3. W. Lipke, Earned Schedule (ES, SPI(t) = ES ÷ AT; o SPI em R$ tende a 1 no fim da obra). Texto em português:
   https://www.earnedschedule.com/Docs/Earned%20Schedule%20-%20Portuguese.pdf. Introdução:
   https://earnedschedule.com/Docs/Lipke%20UT%20Dallas%202014%20-%20ES%20Introduction%20v1.pdf
4. G. Ballard, *The Last Planner System of Production Control*, tese, Univ. of Birmingham, 2000 (PPC; casos acima de
   70% e meta de 90%), https://etheses.bham.ac.uk/4789/
5. Bortolazza e Formoso, "A Quantitative Analysis of Data Collected From the Last Planner System in Brazil", IGLC 14,
   2006 (133 obras, NORIE/UFRGS), https://www.iglc.net/Papers/Details/415
6. PBQP-H/SiAC, Regimento Geral (2021), https://www.gov.br/cidades/pt-br/assuntos/habitacao/pbqp-h/RegimentoGeraldoSIACAtualizadoPortaria577demarode2021CapaOK.pdf;
   controle de materiais, serviços e fornecedores: Sienge, https://sienge.com.br/blog/pbqph/; CBIC, novo regimento,
   https://cbic.org.br/governo-formaliza-novo-regimento-do-siac-pbqp-h/
7. ABNT NBR 14280:2001 (cadastro de acidente do trabalho): TF = acidentes × 1.000.000 ÷ HHT; TG com dias perdidos e
   debitados. Resumo: RSData, https://www.rsdata.com.br/qual-a-diferenca-entre-taxa-de-frequencia-e-taxa-de-gravidade/
8. CBIC, Manual de SST 2021, Anexo A (checklists da NR-18),
   https://cbic.org.br/wp-content/uploads/2022/11/cbicmanualsst2021anexoagrupo01.pdf
9. Retrabalho: FGV Ibre, via Jornal da Obra (até 12% do custo),
   https://jornaldobras.com.br/noticia/117200/falhas-de-qualidade-e-retrabalho-podem-elevar-custo-de-obras-em-ate-12-apontam-especialistas;
   UNESP (1% a 10%), https://repositorio.unesp.br/server/api/core/bitstreams/d339638c-599a-44ee-9f23-325b6f7d80a2/content
10. Lei 13.786/2018 (art. 43-A da Lei 4.591/64, tolerância de 180 dias),
    https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13786.htm; comentário: CBIC,
    https://cbic.org.br/wp-content/uploads/2019/05/2-MELHIM.pdf
11. CBIC, "Taxa de acidentalidade da construção em 2018 é a menor da série" (14,98 por mil vínculos),
    https://cbic.org.br/relacoestrabalhistas/artigo-taxa-de-acidentalidade-da-construcao-em-2018-e-a-menor-da-serie/
12. Indicadores de sustentabilidade do PBQP-H e a falta de valores de referência: ANTAC/SIBRAGEC,
    https://eventos.antac.org.br/index.php/sibragec/article/download/76/72/71
13. INMET, balanço de abril em Natal (normal 1991–2020: 240,5 mm),
    https://portal.inmet.gov.br/noticias/balanço-natal-rn-teve-chuva-abaixo-da-média-em-abril-deste-ano
14. Indicadores de benchmarking de obras (desvio de custo, desvio de prazo, PPC, taxa de frequência): SISIND-NET,
    NORIE/UFRGS, https://revistas.usp.br/gestaodeprojetos/article/download/50916/54996/63379
