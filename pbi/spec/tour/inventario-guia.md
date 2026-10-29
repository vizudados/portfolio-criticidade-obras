# Inventário do guia atual · base do tour guiado

Data: 07/10/2026 · Projeto: `criticidade-obras-bi` · Figma: `FjBWDk5odF9HaZ2pwhGosl`, página `04 · Redesenho v2 · Painel Criticidade de Obras` (`372:685`).

Fontes: `pbi/spec/redesenho/t01.md` a `t04.md`, `brief-v2.md`, `brief-pbi-v2.md`; `docs/03-indicadores-e-criticidade.md`; código em `pbi/scripts/`; PBIP gravado em `pbi/pbip/CO.Report/`.

Convenções: geometria em canvas 1920 × 1080. "Marcador" = o número de 28 px no guia. "Bookmark" = marcador de exibição do Power BI (`T<n>_…_NN`). As coordenadas dos elementos de tela vêm das declarações do código v2 (lidas sem gravar nada) e batem com as specs `t0N.md`.

Esta leitura não alterou nenhum arquivo do projeto. O único arquivo gravado é este.

---

## 0. Resumo

- Quatro telas, 30 itens no total: **T1 = 7, T2 = 9, T3 = 7, T4 = 7**. Cada tela tem um item "Navegação" e um "Filtro e ajuda".
- Os textos dos itens são constantes Python (`GUIA_ITENS` em `leituras_tN.py`), não medidas DAX. A única parte dinâmica é a contagem de obras da T1 (`_txtN`).
- Abre pelo botão `T<n>_Aj_Guia` (1816, 38, 44 × 44), que dispara o bookmark `T<n>_GUIA_01`. Fecha pelo visual `T<n>_Gui_Fora` (tela inteira), que dispara `T<n>_LEITURA_00`. O "×" e o "Fechar" dentro do HTML são só desenho.
- Não há tour por passos no repositório. `pbi/scripts/paginas_ref_outro_projeto/guia.py` é um painel único (§3.7).
- Contexto: a memória do projeto registra o tour por passos, com gestor em 3D (Magnific), como próxima janela. Este inventário cobre só o guia atual.
- Pontos de atenção: o visual que fecha o guia fica acima do HTML (§7.1). A convenção de coordenadas dos marcadores muda entre telas (§7.3).

---

## 1. Regra de pontuação (`docs/03-indicadores-e-criticidade.md`)

Cinco indicadores, pesos somando 100:

| Indicador | Peso | Estável (0) | Atenção (1) | Crítico (2) |
|---|---|---|---|---|
| Resultado da obra (% do orçamento) | 35 | ≥ +1,0% | 0 a +1,0% | < 0 |
| Desvio físico acumulado | 25 | ≥ −1,0 p.p. | −3,0 a −1,0 p.p. | < −3,0 p.p. |
| Desembolso do mês × previsto | 20 | ≤ +10% | +10% a +25% | > +25% |
| Variação do resultado no mês | 10 | ≥ −0,2 p.p. | −0,5 a −0,2 p.p. | < −0,5 p.p. |
| Resultado sem ativos | 10 | ≥ 0 | < 0 | — (nunca crítico sozinho) |

- **Pontuação** = Σ (peso × status) ÷ 2, de 0 a 100. **Crítico ≥ 50 · Atenção 25 a 49 · Estável < 25.**
- **Mobilização:** obra com menos de 10% executado tem status no máximo atenção e pontuação no máximo 49, com selo "em mobilização".
- Os limites são **proposta**, a validar com a diretoria da Construtora (texto da própria doc).
- Dúvida: com "resultado sem ativos" limitado a atenção, o máximo teórico é 95, não 100 (§7.10).
- A régua escrita no guia de T1 e T2 segue esta regra.

---

## 2. Por tela

### T1 · Visão geral · 7 itens

Figma: guia `391:4507`; exemplo "Guia aberto" `391:5956`. Painel do guia: **1120 × 765 em (400, 158)**, centralizado.

| # | Título | Elemento explicado | Geometria canvas (x, y, w, h) | Visuais de âncora (PBIR) |
|---|---|---|---|---|
| 1 | Cartões da carteira | cinco cartões do mês | 352, 109, 1508, 140 (cada cartão 302 × 140 em x 352 · 654 · 955 · 1257 · 1558) | `T1_Kpi_Obras`, `_Resultado`, `_Fisico`, `_Desembolso`, `_SemEstoque` |
| 2 | Obras por criticidade | painel da lista | 352, 273, 1004, 631 | `T1_Obras_Cabecalho` (352, 305) · `T1_Obras_Lista` (352, 369, 1004, 535) |
| 3 | O que pesa na carteira | painel | 1396, 273, 464, 406 | `T1_Pesa_Subtitulo` (1396, 305) · `T1_Pesa_Lista` (1396, 341, 464, 338) |
| 4 | Como os meses evoluíram | painel | 1396, 719, 464, 321 | `T1_Semestre_Subtitulo` (1396, 751) · `T1_Semestre_Colunas` (1396, 787, 464, 236) |
| 5 | Leitura do mês | faixa-síntese | 352, 944, 1004, 96 | `T1_Sintese_Texto` |
| 6 | Filtro e ajuda | recorte em uso, funil, guia e "?" dos painéis | recorte 1180, 48, 552, 24 · funil 1760, 38, 44 × 44 · guia 1816, 38, 44 × 44 · "?" 1328, 272 · 1832, 272 · 1832, 718 (30 × 30) | `T1_Cab_Recorte`, `T1_Cab_Filtros`, `T1_Aj_Guia`, `T1_Aj_Obras`, `T1_Aj_Pesa`, `T1_Aj_Semestre` |
| 7 | Navegação | sidebar de páginas | 32, 234, 248, 200 (quatro vagas de 44 a cada 52: 234 Visão geral = a própria tela, sem botão; 286; 338; 390) | `T1_Nav_T2` (32, 286), `T1_Nav_T3` (32, 338), `T1_Nav_T4` (32, 390) |
| — | Gaveta de filtros (abre pelo funil) | drawer, parte de "Filtro e ajuda" | 12, 12, 680, 1056 (filtros em x 358 a 668): recorte 358, 96, 310, 44 · mês 359, 181, 308, 42 · janela 359, 265, 308, 40 · nota 358, 314 · status 358, 862, 310, 58 · limpar 528, 942, 140, 38 · × 632, 48, 36, 36 | `T1_Drw_*` (oculto até o funil) |

Marcadores (código guarda o centro; desenho de 28 px = centro − 14):

| Nº | Centro | Canto (desenho) | Explica |
|---|---|---|---|
| 1 | 352, 109 | 338, 95 | cartões |
| 2 | 352, 273 | 338, 259 | lista de obras |
| 3 | 1880, 273 | 1866, 259 | o que pesa |
| 4 | 1880, 719 | 1866, 705 | meses |
| 5 | 352, 944 | 338, 930 | leitura do mês |
| 6 | 1760, 38 | 1746, 24 | filtro e ajuda |
| 7 | 32, 234 | 18, 220 | navegação |

Textos (`pbi/scripts/leituras_t1.py`, `GUIA_ITENS` L843–857; título "Como ler esta tela"; sobretítulo "Guia da página · Visão geral"):

1. **Cartões da carteira** — "Cinco números do mês; o escuro é a resposta da pergunta. Passe o mouse: o cartão vira e mostra como é calculado e de onde vem."
2. **Obras por criticidade** — "As {N} obras em ordem de pontos, com os dois sinais que mais pesam. Passe o mouse numa obra para ver os cinco sinais e os pontos mês a mês." ({N} = contagem por extenso, via `_txtN`.)
3. **O que pesa na carteira** — "Pontos somados das {N} obras, por indicador: o vermelho vem das obras críticas, o ocre das obras em atenção. Passe o mouse para ver obra por obra."
4. **Como os meses evoluíram** — "Obras por status, mês a mês, na janela escolhida no filtro (até 12 meses). Passe o mouse num mês para ver quem estava em cada faixa e o que mudou."
5. **Leitura do mês** — "A síntese escrita do mês, embaixo da lista; muda com o filtro."
6. **Filtro e ajuda** — "O topo mostra o recorte em uso. O funil abre os filtros de mês, janela e obras; o "?" redondo abre este guia; o "?" de cada painel abre a leitura daquele gráfico."
7. **Navegação** — "Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as telas."

Intro: "A tela responde em três passos: os cartões dizem como a carteira fechou o mês; a lista ordena as obras da mais crítica à mais estável; a coluna da direita explica o que pesou e como os meses chegaram até aqui."

Régua "A régua de criticidade": crítico · 50 pontos ou mais; atenção · 25 a 49; estável · abaixo de 25; mobilização · menos de 10% executado: a obra fica, no máximo, em atenção. Nota: "Os pontos somam cinco indicadores com pesos diferentes; a leitura de cada painel explica a conta e a faixa de cada um."

### T2 · Análise crítica · 9 itens

Figma: guia `391:6704` (1120 × 771); exemplo "Guia aberto" `391:8032`. Painel do guia: **1120 × 771 em (400, 155)**.

| # | Título | Elemento explicado | Geometria canvas (x, y, w, h) | Visuais de âncora |
|---|---|---|---|---|
| 1 | Cartões da obra | cinco cartões (o escuro é o resultado da obra) | 352, 109, 1508, 140 | `T2_Kpi_Resultado`, `_Anterior`, `_SemEstoque`, `_Fisico`, `_Criticidade` |
| 2 | O quadradinho | painel da conta da planilha | 352, 273, 548, 584 | `T2_Quad_Entradas` (352, 341, 548, 108) · `T2_Quad_Itens` (352, 457, 548, 300) · `T2_Quad_Resultado` (352, 767, 548, 88) |
| 3 | Com e sem estoque | caixa creme com a síntese | 352, 897, 548, 143 | `T2_ComSem_Texto` (372, 936, 508, 92) |
| 4 | Como o resultado se forma | painel cascata | 940, 273, 508, 350 | `T2_Cas_Degraus` (940, 341, 508, 282) |
| 5 | Resultado da obra, mês a mês | painel | 940, 663, 508, 377 | `T2_Mes_Subtitulo` (940, 695) · `T2_Mes_Colunas` (940, 759, 508, 281) |
| 6 | Sinais do mês | painel | 1488, 273, 372, 388 | `T2_Sinais_Subtitulo` (1488, 305) · `T2_Sinais_Lista` (1488, 341, 372, 320) |
| 7 | Desembolso do mês | painel | 1488, 701, 372, 339 | `T2_Des_Html` (1488, 769, 372, 271) |
| 8 | Filtro e ajuda | recorte, funil, guia e "?" | recorte 1180, 48, 552, 24 · funil 1760, 38 · guia 1816, 38 · "?" 872, 272 · 1420, 272 · 1420, 662 · 1832, 272 (30 × 30) | `T2_Cab_Recorte`, `T2_Cab_Filtros`, `T2_Aj_Guia`, `T2_Aj_Quad`, `T2_Aj_Forma`, `T2_Aj_Mes`, `T2_Aj_Sinais` |
| 9 | Navegação | sidebar de páginas | 32, 234, 248, 200 (vaga 286 = Análise crítica, sem botão) | `T2_Nav_T1` (32, 234), `T2_Nav_T3` (32, 338), `T2_Nav_T4` (32, 390) |

Marcadores (código guarda o canto superior-esquerdo; centro = canto + 14):

| Nº | Canto (código) | Centro | Explica | Observação |
|---|---|---|---|---|
| 1 | 338, 95 | 352, 109 | cartões | |
| 2 | 338, 259 | 352, 273 | quadradinho | |
| 3 | 338, 883 | 352, 897 | com e sem estoque | |
| 4 | 926, 259 | 940, 273 | cascata | **fica sob o painel do guia** (a cascata está coberta) |
| 5 | 926, 934 | 940, 948 | mês a mês | |
| 6 | 1838, 259 | 1852, 273 | sinais | |
| 7 | 1838, 687 | 1852, 701 | desembolso | |
| 8 | 1398, 46 | 1412, 60 | filtro e ajuda | |
| 9 | 14, 235 | 28, 249 | navegação | |

Textos (`pbi/scripts/leituras_t2.py`, `GUIA_ITENS` L528–545; título "Como ler esta tela"; sobretítulo "Guia da página · Análise crítica"):

1. **Cartões da obra** — "Cinco números do mês; o escuro é o resultado da obra, a resposta da pergunta. Vermelho é negativo; a marca colorida é o status. Passe o mouse: o cartão vira e mostra a conta."
2. **O quadradinho** — "Os dez itens do bloco de resultado da planilha, na ordem da conta, com valor e fração do orçamento. Passe o mouse num item para ver o que é e as linhas anexadas."
3. **Com e sem estoque** — "A síntese escrita da obra no mês; muda com a obra e o mês escolhidos."
4. **Como o resultado se forma** — "Os degraus da conta: crédito, mais o pago e não aplicado, menos contas a pagar e desembolsado (em vermelho). Passe o mouse num degrau para ver os itens."
5. **Resultado da obra, mês a mês** — "Resultado oficial (barra cheia) e sem estoque e adiantamentos (hachura) na janela escolhida; vermelho quando negativo. Passe o mouse num mês para ver a conta."
6. **Sinais do mês** — "Os cinco indicadores da régua com status, valor, faixa e peso. Passe o mouse num sinal para ver a faixa completa e a trajetória do período."
7. **Desembolso do mês** — "Previsto (creme) × desembolsado (preto) no mês, a diferença e o desvio, com a justificativa exigida acima de ±10%."
8. **Filtro e ajuda** — "O topo mostra a obra e o mês em uso. O funil abre os filtros; o "?" redondo abre este guia; o "?" de cada painel abre a leitura do gráfico."
9. **Navegação** — "Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as telas."

Intro: "Os cartões dizem como a obra fechou o mês; o quadradinho reproduz a conta da planilha; os painéis do meio e da direita mostram de onde vem o resultado, como ele mudou e quais sinais pesam."

Régua "A régua de criticidade": mesmas quatro faixas da T1 (crítico 50 ou mais; atenção 25 a 49; estável abaixo de 25; mobilização).

### T3 · Avanço físico · 7 itens

Figma: guia `395:6438` (1120 × 883); exemplo "Guia aberto" `397:1898`. Painel do guia: **1120 × 883 em (400, 99)**.

| # | Título | Elemento explicado | Geometria canvas (x, y, w, h) | Visuais de âncora |
|---|---|---|---|---|
| 1 | Cartões da obra | cinco cartões da obra em foco (o escuro é o desvio físico) | 352, 109, 1508, 140 | `T3_Kpi_Desvio`, `_Executado`, `_Previsto`, `_NoMes`, `_Termino` |
| 2 | Curva S | painel | 352, 273, 900, 370 | `T3_Curva_Cabecalho` (352, 273, 858, 54) · `T3_Curva_Grafico` (352, 341, 900, 302) · `T3_Curva_Meses` (352, 341, 860, 302) |
| 3 | Ritmo do mês | painel | 1292, 273, 568, 290 | `T3_Ritmo_Cabecalho` (1292, 273, 526, 54) · `T3_Ritmo_Colunas` (1292, 341, 568, 222) |
| 4 | Avanço das obras | painel | 1292, 603, 568, 437 | `T3_Avanco_Cabecalho` (1292, 603, 526, 54) · `T3_Avanco_Lista` (1292, 675, 568, 288) · `T3_Avanco_Legenda` (1292, 971, 568, 61) |
| 5 | Linha do tempo das obras | painel | 352, 683, 900, 357 | `T3_Linha_Cabecalho` (352, 683, 858, 54) · `T3_Linha_Grade` (352, 751, 900, 289) · `T3_Linha_Obras` (352, 779, 900, 230) |
| 6 | Filtro e ajuda | recorte, funil, guia e "?" | recorte 1180, 48, 552, 24 · funil 1760, 38 · guia 1816, 38 · "?" 1224, 272 · 1832, 272 · 1832, 602 · 1224, 682 (30 × 30) | `T3_Cab_Recorte`, `T3_Cab_Filtros`, `T3_Aj_Guia`, `T3_Aj_Curva`, `T3_Aj_Ritmo`, `T3_Aj_Avanco`, `T3_Aj_Linha` |
| 7 | Navegação | sidebar de páginas | 32, 234, 248, 200 (vaga 338 = Avanço físico, sem botão) | `T3_Nav_T1` (32, 234), `T3_Nav_T2` (32, 286), `T3_Nav_T4` (32, 390) |

Marcadores (código guarda o centro; desenho = centro − 14). **Atenção:** a spec `t03.md` não traz as coordenadas dos marcadores. Ver §7.3.

| Nº | Centro (código) | Canto (desenho) | Explica |
|---|---|---|---|
| 1 | 338, 124 | 324, 110 | cartões |
| 2 | 338, 288 | 324, 274 | curva S |
| 3 | 1880, 288 | 1866, 274 | ritmo |
| 4 | 1880, 618 | 1866, 604 | avanço |
| 5 | 338, 698 | 324, 684 | linha do tempo |
| 6 | 1412, 60 | 1398, 46 | filtro e ajuda |
| 7 | 26, 230 | 12, 216 | navegação |

Textos (`pbi/scripts/leituras_t3.py`, `GUIA_ITENS` L840–856; título "Como ler esta tela"; sobretítulo "Guia da página · Avanço físico"):

1. **Cartões da obra** — "Cinco números da obra em foco; o escuro, o desvio físico acumulado, é a resposta da pergunta. Passe o mouse: o cartão vira e mostra como é calculado e de onde vem."
2. **Curva S** — "Previsto (tracejado) e executado (sólido) acumulados, mês a mês; a área entre as linhas é o atraso. Passe o mouse num mês para ver o acumulado, o ritmo e o dinheiro daquele mês."
3. **Ritmo do mês** — "O que o cronograma pedia e o que a obra fez em cada mês, em % do orçamento. Passe o mouse para ver o previsto do mês, o acumulado e a justificativa da planilha."
4. **Avanço das obras** — "Executado e previsto de cada obra, com o desvio e a marca da régua; a cor da barra é a faixa do desvio físico e a obra em foco vem destacada. Passe o mouse para ver o desvio mês a mês."
5. **Linha do tempo das obras** — "Início e término previsto das obras em andamento e das quatro a entrar, tracejadas, com orçamento legal da cronograma; a linha vertical é o mês de referência. Passe o mouse numa obra para ver prazo, orçamento e físico contra financeiro."
6. **Filtro e ajuda** — "O topo mostra a obra e o mês em uso. O funil abre os filtros; o "?" redondo abre este guia; o "?" de cada painel abre a leitura daquele gráfico."
7. **Navegação** — "Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as telas."

Intro: "A tela responde em dois planos: em cima, a obra em foco — os cartões e a curva S dizem se ela está no ritmo e desde quando não está; embaixo e à direita, a carteira — quem está à frente, quem está atrás e o que entra no canteiro."

Régua "A régua do desvio físico": crítico · abaixo de −3,0 p.p.; atenção · −3,0 a −1,0 p.p.; estável · −1,0 p.p. ou mais; mobilização · menos de 10% executado. Nota: "O desvio físico vale 25 dos 100 pontos da criticidade da obra; a pontuação completa e os outros quatro sinais estão na Visão geral."

### T4 · Resultado no tempo · 7 itens

Figma: guia `391:6757` (1120 × 920); exemplo "Guia aberto" `391:9696`. Painel do guia: **1120 × 920 em (400, 80)**.

| # | Título | Elemento explicado | Geometria canvas (x, y, w, h) | Visuais de âncora |
|---|---|---|---|---|
| 1 | Cartões do mês | cinco cartões (o escuro é o resultado da carteira) | 352, 109, 1508, 140 | `T4_Kpi_Resultado`, `_MesAnterior`, `_SemEstoque`, `_Desembolso`, `_Justificativas` |
| 2 | Resultado da carteira, mês a mês | painel | 352, 273, 1068, 380 | `T4_Mes_Colunas` (352, 341, 1068, 312) |
| 3 | Resultado por obra | painel | 1460, 273, 400, 380 | `T4_Obra_Cabecalho` (1460, 305, 400, 52) · `T4_Obra_Lista` (1460, 365, 400, 289) |
| 4 | Desembolso da carteira | painel | 352, 693, 1068, 347 | `T4_DesCart_Colunas` (352, 761, 1068, 279) |
| 5 | Desembolso do mês por obra | painel | 1460, 693, 400, 347 | `T4_DesObra_Titulo` (1460, 693, 360, 28) · `T4_DesObra_Cabecalho` (1460, 761, 400, 15) · `T4_DesObra_Lista` (1460, 785, 400, 253) |
| 6 | Filtro e ajuda | recorte, funil, guia e "?" | recorte 1180, 48, 552, 24 · funil 1760, 38 · guia 1816, 38 · "?" 1392, 272 · 1832, 272 · 1392, 692 · 1832, 692 (30 × 30) | `T4_Cab_Recorte`, `T4_Cab_Filtros`, `T4_Aj_Guia`, `T4_Aj_Mes`, `T4_Aj_Obra`, `T4_Aj_DesCart`, `T4_Aj_DesObra` |
| 7 | Navegação | sidebar de páginas | 32, 234, 248, 200 (vaga 390 = Resultado no tempo, sem botão) | `T4_Nav_T1` (32, 234), `T4_Nav_T2` (32, 286), `T4_Nav_T3` (32, 338) |

Marcadores (código guarda o centro; desenho = centro − 13):

| Nº | Centro | Canto (desenho) | Explica |
|---|---|---|---|
| 1 | 336, 124 | 323, 111 | cartões |
| 2 | 336, 286 | 323, 273 | mês a mês |
| 3 | 1884, 286 | 1871, 273 | resultado por obra (margem direita) |
| 4 | 336, 706 | 323, 693 | desembolso da carteira |
| 5 | 1884, 706 | 1871, 693 | desembolso por obra (margem direita) |
| 6 | 1398, 60 | 1385, 47 | filtro e ajuda |
| 7 | 27, 231 | 14, 218 | navegação |

Textos (`pbi/scripts/leituras_t4.py`, `GUIA_ITENS` L754–773; título "Como ler esta tela"; sobretítulo "Guia da página · Resultado no tempo"):

1. **Cartões do mês** — "Resultado da carteira (o escuro é a resposta), mês anterior, sem estoque e adiantamentos, desembolso e justificativas. Passe o mouse: o cartão vira e mostra como é calculado e de onde vem."
2. **Resultado da carteira, mês a mês** — "Barra cheia: o resultado; barra hachurada: o resultado sem estoque e adiantamentos; vermelho é negativo. Passe o mouse num mês para ver a contribuição de cada obra e o que foi pago e ainda não aplicado."
3. **Resultado por obra** — "Resultado em % do orçamento no mês e variação sobre o mês anterior. Passe o mouse numa obra para ver a tendência do período (o trecho abaixo de zero fica vermelho) e o sem estoque."
4. **Desembolso da carteira** — "Previsto (creme) × desembolsado (preto), mês a mês, com o desvio em cima. Passe o mouse num mês para ver previsto × desembolsado obra por obra."
5. **Desembolso do mês por obra** — "Previsto, desembolsado e desvio; o quadrado tracejado vermelho avisa que a justificativa exigida ficou em branco. Passe o mouse numa obra para ver a justificativa do mês e o histórico."
6. **Filtro e ajuda** — "O topo mostra o recorte em uso. O funil abre os filtros de mês e obra; o "?" redondo abre este guia; o "?" de cada painel abre a leitura daquele gráfico."
7. **Navegação** — "Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as telas."

Intro: "A tela responde em dois tempos. Em cima, o resultado: como a carteira chegou ao número do mês e qual obra puxa para cada lado. Embaixo, o gasto: se a carteira desembolsou além do previsto e se cada obra explicou."

Bloco "As faixas desta tela" (no lugar da régua): Resultado da obra — crítico abaixo de 0; atenção 0 a +1,0%; estável +1,0% ou mais. Desembolso × previsto — crítico acima de +25%; atenção +10% a +25%; estável até +10%; mobilização (menos de 10% executado). Nota: "Vermelho é resultado, variação ou sem estoque negativo; desembolso abaixo do previsto fica na cor da faixa. A hachura marca só o sem estoque. A pontuação de 0 a 100 está na Visão geral; aqui cada marca segue a faixa do indicador, e o desvio acima de ±10% exige justificativa."

### Quadro-resumo

| Tela | Itens | Painel do guia (x, y, w, h) | Marcadores | Medida DAX |
|---|---|---|---|---|
| T1 | 7 | 400, 158, 1120, 765 | 7 | `T1 · Guia · HTML` |
| T2 | 9 | 400, 155, 1120, 771 | 9 | `T2 · Guia · HTML` |
| T3 | 7 | 400, 99, 1120, 883 | 7 | `T3 · Guia · HTML` |
| T4 | 7 | 400, 80, 1120, 920 | 7 | `T4 · Guia · HTML` |

Alturas: as que a spec registra (medidas no Figma). No PBI o painel é centralizado por CSS (`top: 50%; translateY(-50%)`), então a altura real depende do conteúdo renderizado.

---

## 3. Implementação atual no Power BI

### 3.1 Medidas DAX

| Medida | Arquivo `.dax` (gravado) | Gerada por | Observação |
|---|---|---|---|
| `T1 · Guia · HTML` | `pbi/dax/T1/Leituras/Leituras/T1 · Guia · HTML.dax` · TMDL `pbip/CO.SemanticModel/definition/tables/_Medidas.tmdl:3250` | `pbi/scripts/leituras_t1.py`: `GUIA_ITENS` L843, `GUIA_MARCAS` L860, `guia_html()` L864, `desenho(...)` L899 | lê `[Recorte · obras no recorte]` (`_Medidas.tmdl:1564`, = `[Obras com análise · ref]`); itens 2 e 3 usam a contagem por extenso (`ext()` L51–57 gera o `SWITCH`; `_txtN` em L881) |
| `T2 · Guia · HTML` | `pbi/dax/T2/Leituras/Leituras/T2 · Guia · HTML.dax` · TMDL `_Medidas.tmdl:6928` | `pbi/scripts/leituras_t2.py`: `GUIA_ITENS` L528, `GUIA_MARCAS` L548, `guia_html()` L552, `desenho(...)` L573 | texto fixo |
| `T3 · Guia · HTML` | `pbi/dax/T3/Leituras/T3 · Guia · HTML.dax` · TMDL `_Medidas.tmdl:10492` | `pbi/scripts/leituras_t3.py`: `GUIA_ITENS` L840, `GUIA_MARCAS` L859, `guia_html()` L862, `desenho(...)` L890 | texto fixo |
| `T4 · Guia · HTML` | `pbi/dax/T4/Leituras/T4 · Guia · HTML.dax` · TMDL `_Medidas.tmdl:15214` | `pbi/scripts/leituras_t4.py`: `GUIA_ITENS` L754, `GUIA_MARCAS` L776, `guia_html()` L780, `desenho(...)` L812 | texto fixo |
| `T1 · Leitura · CSS` | `pbi/dax/T1/…` | `leituras_t1.py`: `CSS_GUIA` L966 (CSS das leituras em `CSS_LEITURA` L906); `desenho` só dentro de `__main__` (L1002) | CSS compartilhado pelas leituras e pelo guia |
| `T2 · Leitura · CSS` | `pbi/dax/T2/…` | `leituras_t2.py`: `CSS_GUIA` L143; `desenho` L170 | — |
| `T3 · Leitura · CSS` | `pbi/dax/T3/…` | `leituras_t3.py`: `CSS_GUIA` L958; `desenho` L990 | — |
| `T4 · Leitura · CSS` | `pbi/dax/T4/…` | `leituras_t4.py`: `CSS_GUIA_T4` L894; `desenho` só dentro de `__main__` (L931) | — |

Gravação: `leituras_t1.py` e `leituras_t2.py` gravam em `pbi/dax/TN/Leituras` (arquivo em `Leituras/Leituras/`). `leituras_t3.py` e `leituras_t4.py` gravam em `pbi/dax/TN` (arquivo em `Leituras/`). Isso sai do `gravar()` com o `@pasta` do cabeçalho.

Regeneração: rodar `python -X utf8 pbi/scripts/leituras_tN.py` para cada tela. Os módulos T1 e T4 só gravam os CSS dentro de `__main__`; por isso rode o arquivo, não o importe.

### 3.2 Visuais PBIR do guia (mesmos nomes e posições nas quatro telas)

Declarados por `declarar_tela()` em `pbi/scripts/leituras_lib.py` (L25–75). Os nomes são `T<n>_…`.

| Visual | Tipo | x, y, w, h | z | tab | Oculto | Ação / conteúdo | Código |
|---|---|---|---|---|---|---|---|
| `T<n>_Aj_Guia` | actionButton | 1816, 38, 44, 44 | 1080 | 32 | não | bookmark `T<n>_GUIA_01`; realce `#E9E0CF`, raio 10 | `leituras_lib.py` L55–57 |
| `T<n>_Gui_Html` | HTML Content (STANDALONE 2.0) | 0, 0, 1920, 1080 | 6000 | 720 | sim | medida `T<n> · Guia · HTML`; folha `T<n> · Leitura · CSS`; alt "Guia da página …" | `leituras_lib.py` L50–52 |
| `T<n>_Gui_Fora` | actionButton (transparente) | 0, 0, 1920, 1080 | 6001 | 721 | sim | bookmark `T<n>_LEITURA_00`; dica "Fechar o guia" | `leituras_lib.py` L53–54 |

- `Z_GUIA = 6000` (`leituras_lib.py` L22). Camadas em `pbip_lib.py` L69: conteúdo 300, ação 1020, leitura 4000, drawer 5000, navegação 5500.
- **Não há visual de véu separado.** O véu é o CSS `.gv` dentro do HTML do `Gui_Html`.
- O "×" (`.gv .x`) e o "Fechar" (`.rod .fe`) são texto do HTML, sem ação.
- O desenho do botão "?" redondo está na casca (`pbi/spec/casca/_fonte_v2/T<n>.svg`, grupo `Ajuda · Guia da página`). O visual `T<n>_Aj_Guia` é a área transparente sobre ele.

### 3.3 Bookmarks

| Bookmark | Mostra | Oculta | Grupo | Código |
|---|---|---|---|---|
| `T<n>_GUIA_01` (título "T<n> · guia da página") | `Gui_Html`, `Gui_Fora` | todos os outros visuais de leitura | `("leituras", "Leituras")` | `leituras_lib.py` L70–72 |
| `T<n>_LEITURA_00` (título "leituras fechadas") | nenhum | todos, inclusive `Gui_*` | `Leituras` | L73–74 |
| `T<n>_LEITURA_<CHAVE>_01` | o painel `Lei_<chave>`, seu × (`LeiX_`), `Lei_Fora` | o restante | `Leituras` | L65–69 |

Chaves: T1 `OBRAS`, `PESA`, `SEMESTRE`; T2 `QUAD`, `FORMA`, `MES`, `SINAIS`; T3 `CURVA`, `RITMO`, `AVANCO`, `LINHA`; T4 `MES`, `OBRA`, `DESCART`, `DESOBRA`.

Os bookmarks são só de exibição: `applyOnlyToTargetVisuals`, `suppressData`, `suppressActiveSection` (`pbip_lib.py` L765–781). Não mexem em filtro, página nem dado.

Verificado nos arquivos gravados em `pbi/pbip/CO.Report/definition/bookmarks/`: `T<n>_GUIA_01.bookmark.json` mostra só `Gui_Html` e `Gui_Fora`, e oculta os visuais de leitura.

### 3.4 Como abre e fecha hoje

1. Clique em `T<n>_Aj_Guia` (1816, 38).
2. O bookmark `T<n>_GUIA_01` mostra `Gui_Html` e `Gui_Fora`, e fecha qualquer leitura aberta.
3. O HTML desenha o véu fixo (55%), o painel de 1120 centralizado e os marcadores com animação de entrada. Atraso entre marcadores: 90 ms em T1 e T4, 80 ms em T2, 100 ms em T3.
4. Fechamento: clique em qualquer ponto do canvas, pelo `Gui_Fora` (z 6001), que dispara `T<n>_LEITURA_00`. Ver §7.1.

### 3.5 Véu

Vem do CSS do HTML: `.gv{position:fixed;inset:0;background:rgba(11,11,12,.55)}`. Painel: `.gv .gp` com `left:400px; top:50%; transform:translateY(-50%); width:1120px; padding:42px 44px 40px; background:#F7F4EE; border-radius:20px; box-shadow:0 24px 60px rgba(0,0,0,.35)`. Fonte da CSS: `CSS_GUIA` em cada `leituras_tN.py` (ver §3.1).

### 3.6 Textos dos itens

São constantes Python (`GUIA_ITENS`), montadas em `guia_html()`. Trocar o texto = editar `leituras_tN.py` e rodar o gerador. Só a T1 tem parte dinâmica (`_txtN`, a contagem de obras).

### 3.7 Referência de outro projeto: `pbi/scripts/paginas_ref_outro_projeto/guia.py`

- **Não é tour por passos.** É um painel único por tela, com véu e um "×" de fechamento.
- Não roda como está: importa `gerar_guia as GG` (L14), e esse módulo não existe no repositório. Usa `GG.VISUAL` e `GG.FECHAR`.
- Visuais: `<T>_Guia_Painel` (HTML em 276, 12, 1632 × 1056, com o painel em 1420, 108, 464 de largura; segundo a docstring, L5), `<T>_Guia_Veu` (L29, `276, 12, 1144, 1056`), `<T>_Guia_Fechar` (`GG.FECHAR`, em 1830, 118, 40 × 40; docstring). Bookmarks `<T>_GUIA_01` / `<T>_GUIA_00` (L37–40), com `bookmark_exibicao`.
- Reaproveitável: (a) o par de bookmarks abrir/fechar; (b) o véu que cobre só a área à esquerda do painel, para que clique dentro do painel não feche; (c) um botão de fechar real sobre o "×", em vez de texto.
- A árvore `paginas_ref_outro_projeto/` tem outros módulos, mas nenhum deles faz passos (busca por "tour", "passo" e "step" sem resultado útil).

### 3.8 Estado no disco (`pbi/pbip/CO.Report`, manifesto `pbi/spec/relatorio/_gerenciados.json`, gerado em 07/10/2026 13:51:59)

- Os visuais `T<n>_Aj_Guia`, `T<n>_Gui_Html`, `T<n>_Gui_Fora` existem nas quatro telas, com as mesmas posições e z (1816, 38; 0, 0, 1920, 1080; z 6000 e 6001).
- Os bookmarks `T<n>_GUIA_01` e `T<n>_LEITURA_00` existem nas quatro telas.
- As quatro medidas `T<n> · Guia · HTML` estão em `_Medidas.tmdl`. A descrição da T1 é a mesma do código (`leituras_t1.py` L900). O corpo das medidas não foi comparado linha a linha com a saída do gerador.

---

## 4. Mecânica no `montar_pbip.py` e `pbip_lib.py`, e como adicionar bookmarks

### 4.1 Pipeline das declarações

- `montar_pbip.py` L95 `carregar_declaracoes()`: importa, em ordem alfabética, todo `pbi/scripts/paginas/*.py` que não começa com `_`, e chama `declarar(ctx)`. Cada um devolve uma lista de `Pagina`, `Visual`, `Bookmark` ou `Recurso`. Hoje: `comum`, `drawer`, `leituras_t1`–`t4`, `t1`–`t4` e `tt_t1`–`tt_t4`. Um módulo novo entra sem mudar o montador.
- `conferir()` L130: toda medida e coluna projetada existe no TMDL (regra L018); o alvo de cada bookmark existe na página; o bookmark de cada botão existe; a página de cada `PageNavigation` existe.
- `plano()` L179: escreve `definition/pages/<T>/visuals/<nome>/visual.json`, `definition/bookmarks/<nome>.bookmark.json` (L242) e `definition/bookmarks/bookmarks.json`, com os grupos (`grupo`) em L236–249.
- `main()` L311: `--aplicar` (exige Desktop fechado, senão sai com código 3; backup em `pbi/_backups`; grava; atualiza o manifesto; roda `pbir validate`); `--conferir` (sai com 1 se disco ≠ plano); `--ativa <página>`; `--sem-modulo <nome>`.

### 4.2 Funções de construção (`pbi/scripts/pbip_lib.py`)

| Função | Linha | Uso |
|---|---|---|
| `acao_bookmark(nome)` | L279 | `("Bookmark", nome)` |
| `acao_navegar(pagina)` | L275 | `("PageNavigation", pagina)` |
| `visual_botao(...)` | L298 | actionButton com `visualLink`; parâmetros `realce`, `raio`, `oculto`, `z`, `tab`, `dica` |
| `visual_html(...)` | L624 | HTML Content; `folha_de_estilo` (medida CSS), `oculto`, `z`, `tab`, `alt` |
| `bookmark_exibicao(nome, pagina, {visual: bool}, titulo)` | L765 | só visibilidade; nome `T<n>_<ASSUNTO>_<NN>` |
| `class Bookmark(doc, grupo)` | L871–874 | `grupo` = `(nome, displayName)` |
| `pagina_tooltip(...)` | L795 | página de tooltip (`tt<TELA><Assunto>`) |
| `ACOES` | L271 | só `PageNavigation`, `Bookmark`, `ClearAllSlicers` |
| `CAMADAS` | L69 | z por camada |
| `RE_NOME_VISUAL` | L73 | `^(T[1-7]|TT)_[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9]+$` |
| `RE_BOOKMARK` | L77 | `^T[1-7]_[A-Z0-9]+(?:_[A-Z0-9]+)*_\d{2}$` |
| `MAX_NOME_VISUAL` / `MAX_ALT` | L79–80 | 50 caracteres / 250 caracteres |

### 4.3 Como adicionar um tour por passos (proposta, nada implementado)

1. **Textos e medidas.** Um card por passo. Cada card é uma medida HTML (`T<n> · Tour · Passo NN · HTML`), gerada por um módulo novo em `pbi/scripts/` (ex.: `tour_tN.py`) com o mesmo padrão de `leituras_tN.py`. Os textos ficam em constantes Python, como `GUIA_ITENS`.
2. **Visuais.** Por passo, um `visual_html("T<n>_Tour…", x, y, w, h, medida, folha_de_estilo=…, oculto=True, z=…)`. Botões "Anterior", "Próximo" e "Fechar" com `visual_botao(..., acao_bookmark("T<n>_TOUR_NN"))`. O botão "Fechar" deve ficar **abaixo** do card no z, como as leituras (`Lei_Fora` 3990 < 4000). Ver §7.1.
3. **Bookmarks.** Um por passo: `Bookmark(bookmark_exibicao("T<n>_TOUR_NN", "T<n>", {visual: bool, ...}, titulo=...), grupo=("tour", "Tour"))`. Listar só os visuais que mudam de estado.
4. **Ponto de entrada.** Trocar a ação de `T<n>_Aj_Guia` (`leituras_lib.py` L55–57) para o `T<n>_TOUR_01`, ou acrescentar um botão novo.
5. **Destaques.** Decidir a convenção de coordenadas dos marcadores antes (§7.3). Reaproveitar o estilo `.mc` (28 px) do guia.
6. **Validação.** `montar_pbip.py` (simulação) acusa bookmark ou alvo inexistente. Bookmarks não tocam dado, filtro nem página.
7. **Limite.** Um bookmark não troca o conteúdo de um visual. Cada passo precisa do seu próprio HTML, e os botões têm de apontar para bookmarks nomeados. Não existe "próximo" relativo.

---

## 5. Ciclo de build e prova

Ordem documentada (`pbi/scripts/ciclo.sh`, `brief-pbi-v2.md` §5). Todos os comandos rodam a partir da raiz `criticidade-obras-bi`.

```
# 1. Geradores das leituras e do guia (uma vez por tela)
python -X utf8 pbi/scripts/leituras_t1.py
python -X utf8 pbi/scripts/leituras_t2.py
python -X utf8 pbi/scripts/leituras_t3.py
python -X utf8 pbi/scripts/leituras_t4.py

# 2. Lint conta × desenho (exige 0 ERRO)
python -X utf8 pbi/scripts/lint_conta_desenho.py pbi/dax --so-erros
#    opções: --detalhe  --json <arq>  --largura 120  --aninhamento 3  --desenho <regex>

# 3. Modelo (TMDL)
python -X utf8 pbi/scripts/gerar_modelo.py              # simulação: plano + lint TOM
python -X utf8 pbi/scripts/gerar_modelo.py --aplicar    # grava (Desktop fechado; backup em pbi/_backups)
python -X utf8 pbi/scripts/gerar_modelo.py --conferir   # disco × plano
#    opções: --sem-tom (pula lint TOM)  --sem-pasta <nome>

# 4. Relatório (PBIR)
python -X utf8 pbi/scripts/montar_pbip.py               # simulação: plano + conferência
python -X utf8 pbi/scripts/montar_pbip.py --aplicar [--ativa T1] [--sem-modulo t3 --sem-modulo tt_t3]
python -X utf8 pbi/scripts/montar_pbip.py --conferir    # sai com 1 se disco ≠ plano
#    --aplicar: backup, grava, manifesto, pbir validate; sai com 3 se o Desktop estiver aberto no projeto
```

**Desktop** (PowerShell 7, `pwsh`; script `pbi/scripts/desktop.ps1`; só mexe na instância cujo título ou linha de comando bate com o `.pbip`; nunca salva):

```
pwsh -NoProfile -File pbi/scripts/desktop.ps1 -Acao fechar
pwsh -NoProfile -File pbi/scripts/desktop.ps1 -Acao abrir [-Espera 360] [-Reabrir] [-SemRefresh]
pwsh -NoProfile -File pbi/scripts/desktop.ps1 -Acao foto -Saida qa\redesenho\<arq>.png
pwsh -NoProfile -File pbi/scripts/desktop.ps1 -Acao porta | refresh | listar | checar | minimizar
```
Opções: `-Pbip <arq>` (padrão: primeiro `.pbip` da pasta `pbip/`), `-Titulo`, `-ArquivoPorta` (padrão `pbi/qa/porta.txt`, hoje `58272`), `-SaidaContagem`. Códigos de saída: 0 ok · 1 instância não encontrada ou tempo esgotado · 2 erro.

**Fotos de tela (com Desktop aberto):**

```
pwsh -NoProfile -File pbi/scripts/fotos/fotos_desktop.ps1 [-Paginas T1,T2,T3,T4] [-Prefixo v2] [-SemModelo]
#   ATENÇÃO: este script também GRAVA o modelo e o relatório (gerar_modelo --aplicar e montar_pbip --aplicar)
#   antes de fotografar cada página. Saída: pbi/qa/redesenho/desktop/<prefixo>-<pagina>.png

python -X utf8 pbi/scripts/fotos/foto_t1.py tela [--v2] [--drawer] [--lista-aberta] [--verso] [--saida <nome>]
python -X utf8 pbi/scripts/fotos/foto_t2.py tela [--abertos T2_Gui_Html,T2_Gui_Fora] [--wp <svg>] [--dir <pasta>] [--janela 12] [--obra REDINHA] [--ref AAAA-MM]
python -X utf8 pbi/scripts/fotos/foto_t3.py tela [--abertos T3_Gui_Html,T3_Gui_Fora] [--papel <svg>] [--dir <pasta>]
```
- `--abertos` mostra visuais ocultos na foto (`foto_t2.py` L172, L210–214). Serve para fotografar o guia aberto: `T<n>_Gui_Html,T<n>_Gui_Fora`.
- As fotos leem o modelo com `DEFINE MEASURE` (só leitura, L066).
- Para abrir o guia já montado no PBIP (só foto, nunca no arquivo final): `QA_LEITURA=<T1..T4>` abre as leituras (`leituras_lib.py` L59). Não existe equivalente para o guia (o `QA_GUIA` só existe na referência de outro projeto).

**Sequência completa:** `pbi/scripts/ciclo.sh` (ver §7.8 sobre dois scripts ausentes).

---

## 6. Cores e tipografia v2

Fonte: `brief-v2.md` §3 e §5, e a CSS dos módulos de guia. Famílias no código: `Barlow U` (embutida em `desenho_comum.py` L58) e `Segoe UI`.

### 6.1 Tokens de cor (coleção `Construtora · Painel v2`, modo Claro)

| Token | Hex | Uso |
|---|---|---|
| base/preto | `#0B0B0C` | texto principal, cartão escuro, marcador, botão |
| base/grafite | `#3B3B3F` | texto secundário, régua |
| base/creme | `#E9E0CF` | previsto, verso, realce de botão, divisória |
| base/offwhite | `#F7F4EE` | fundo do guia e da leitura, tooltip, fundo da tela |
| base/branco | `#FFFFFF` | prancheta; fundo do corpo do tooltip |
| texto/terciario | `#6B6B70` | eixo, nota, sobretítulo |
| linha/divisor | `#E9E0CF` | divisória creme entre painéis |
| linha/regra | `#E1E1E1` | regras e traços |
| linha/trilha | `#EFEFEF` | trilho de barra |
| status/critico | `#C43737` | crítico (sólido) |
| status/critico-claro | `#F7E3E3` | fundo de linha crítica |
| status/atencao | `#C9821F` | atenção (sólido) |
| status/atencao-claro | `#F6E7CF` | — |
| status/atencao-texto | `#8A5A0B` | — |
| status/estavel | `#A9CDB9` | estável (sólido, recua) |
| status/estavel-claro | `#E1EFE7` | — |
| status/estavel-texto | `#1E5C43` | — |
| status/estavel-borda | `#6E9F85` | contorno da barra estável |
| valor/negativo | `#C43737` | negativo sobre claro |
| valor/negativo-sobre-creme | `#A82C2C` | negativo sobre creme |
| valor/negativo-sobre-preto | `#F2877C` | negativo sobre preto |
| mobilização | tracejado `base/grafite` | marca tracejada (`[3, 2]`) |

Sombras (estilos de efeito): `v2/Sombra · tooltip`, `v2/Sombra · leitura` (CSS: `0 12px 32px rgba(0,0,0,.22)`), `v2/Sombra · guia` (CSS: `0 24px 60px rgba(0,0,0,.35)`).

Regra de cor do guia: vermelho só para resultado, variação e sem estoque negativos (`brief-pbi-v2.md` §1). Desvio de desembolso abaixo do previsto não é vermelho. Limite de régua ou faixa nunca é vermelho.

### 6.2 Estilos de texto v2

| Estilo | Fonte | Tamanho / altura | Uso |
|---|---|---|---|
| Página · título | Barlow SB | 38 / 44 | título da tela; título do guia (`.gv .tit`) |
| Pergunta | Segoe | 19 / 24 | pergunta ao lado do título |
| Cartão · rótulo | Barlow SB | 15 / 18, caixa normal | título do cartão |
| Cartão · número | Barlow SB | 42 / 50 | número do cartão |
| Cartão · lado | Barlow Medium | 17 / 21 | ao lado do número |
| Painel · título | Barlow SB | 23 / 28 | título do painel |
| Subtítulo | Segoe | 15 / 20 | subtítulo do painel |
| Destaque · nome | Barlow SB | 21 / 26 | nome na lista, título do tooltip |
| Valor | Barlow SB | 16 / 20 | valor em linha |
| Valor · gráfico | Barlow SB | 14 / 17 | rótulo de dado |
| Texto | Segoe | 15 / 21 | corpo, detalhe |
| Texto · forte | Segoe SB | 15 / 21 | rótulo de linha |
| Texto · apoio | Segoe | 14 / 19 | contexto, nota |
| Eixo | Segoe | 13 / 16 | eixo (único Segoe abaixo de 14) |
| Chip | Barlow SB | 13, caixa alta, 8% | chips |
| Versalete | Barlow SB | 12, caixa alta, 10% | cabeçalho de coluna, micro-rótulo (piso geral 12) |
| Leitura | Segoe | 17 / 26 | texto da leitura e do guia |
| Achado | Barlow SB | 34 / 40 | número de destaque na leitura |
| Sidebar · item | Segoe | 17 / 22 | navegação |

Guia (CSS atual, `leituras_tN.py`): itens — nome Barlow SB 16 / 20; descrição Segoe 15 / 21 em `#3B3B3F`; número do item 16 px em círculo de 28 px (fundo `#0B0B0C`, texto `#F7F4EE`); régua 15 / 21; "Fechar" em pílula de 112 × 40, raio 20, fundo `#0B0B0C`, texto `#F7F4EE`, Barlow SB 16. Marcador `.mc`: 28 px, círculo `#0B0B0C`, contorno 2 px `#F7F4EE`, Barlow SB 16.

### 6.3 Sugestão para o card do tour (a validar)

- Fundo `#F7F4EE`; contorno 1 px `#0B0B0C`; raio 20 (como o guia) ou 0 (como o tooltip); sombra `0 24px 60px rgba(0,0,0,.35)`.
- Véu `rgba(11,11,12,.55)`, o mesmo do guia.
- Título e passos com Barlow SB 38/44 e Segoe 17/26, seguindo o guia.
- Botões: primário em pílula `#0B0B0C` com texto `#F7F4EE`; secundário com contorno 1 px `#0B0B0C`; realce no hover `#E9E0CF`.
- Marcador/destaque: círculo de 28 px `#0B0B0C` com contorno `#F7F4EE`.

---

## 7. Achados, riscos e o que não foi verificado

1. **O guia fecha com qualquer clique.** `T<n>_Gui_Fora` (z 6001) fica **acima** de `T<n>_Gui_Html` (z 6000) e cobre a tela inteira. Pelo código, clique no painel também fecha. As leituras fazem o contrário (`Lei_Fora` z 3990, abaixo do HTML de z 4000+). Confirmar no Desktop. Para o tour, o fechamento precisa ficar abaixo do card ou cobrir só a área fora dele (como a referência de outro projeto).
2. **"×" e "Fechar" do guia não são botões.** São texto do HTML. Só o véu fecha. O tour precisa de botões nativos (`visual_botao`).
3. **Convenção de coordenadas dos marcadores diverge.** T2 guarda o canto superior-esquerdo e desenha sem subtrair (`leituras_t2.py` L548–549, L558). T1 guarda o centro e subtrai 14 (L860, L870). T3 guarda o centro e subtrai 14 (L859, L866–868). T4 guarda o centro e subtrai 13 (L776, L786). T1 e T2 coincidem. Em T3 a coluna esquerda (338, usada em 1, 2 e 5) provavelmente fica 14 px deslocada, porque 338 parece canto. A `t03.md` não tem coordenadas dos marcadores para conferir. Confirmar com a foto `t03-guia.png`.
4. **Texto de outros documentos está defasado.** `docs/06-interacoes-spec.md` §1.8 e §5 (guia v1: 760 × 858, "FOLHA 0X", marcadores em outra disposição). `leituras_t1.py` L13 diz "painel 760". A referência do v2 é `pbi/spec/redesenho/t0N.md` §2 e §3.
5. **`paginas_ref_outro_projeto/guia.py` não roda como está** (`gerar_guia` ausente) e não é tour. Ver §3.7.
6. **`pbi/scripts/pagina_comum.py` (raiz) é código morto:** nenhum módulo o importa.
7. **`pbi/scripts/fotos/fotos_desktop.ps1` grava o projeto.** Ele roda `gerar_modelo.py --aplicar` e `montar_pbip.py --aplicar` antes de fotografar. Não é só foto. Os agentes da tela não devem rodá-lo (o brief proíbe `--aplicar`).
8. **`pbi/scripts/ciclo.sh` referencia dois scripts que não existem:** `gerar_t3_js.py` e `gerar_t7_js.py` (cópia de outro projeto). A falha aparece só como uma linha (`head -1` ou `tail -1`), e o `set -e` não para o script, porque o status do pipeline é o do `head`/`tail`. O comportamento está certo para o Construtora (pega o `.pbip` de `pbip/`).
9. **Mapa das pastas de DAX do guia** é inconsistente (T1 e T2 em `Leituras/Leituras/`, T3 e T4 em `Leituras/`). Não quebra nada, mas dificulta achar os arquivos.
10. **Regra de pontuação:** com "resultado sem ativos" limitado a atenção, o máximo é 95. A doc diz "0 a 100". Confirmar a regra com o Alisson antes de escrever "100" no tour.
11. **Não verificado:** renderização no Desktop; comportamento de clique do véu (§7.1); se o corpo das medidas no TMDL bate com o gerador; se o guia do PBIP em disco tem o texto v2 (só nome, posição e bookmarks foram conferidos).
12. **Efeitos colaterais desta leitura:** o script de leitura importou `montar_pbip` e as declarações (sem `--aplicar`). Pode ter atualizado `pbi/scripts/__pycache__`. Dois PNG de `assets/personagem/modelo/` (`modelo-v1.png`, `modelo-v2.png`) tiveram a data de modificação posterior ao início desta leitura. Esta leitura não os abriu nem gravou, e a origem da mudança não foi apurada.
13. **Sobre marcadores e painéis:** o "?" de cada painel tem 30 × 30 no código e 26 × 26 na spec (`t0N.md`). Diferença pequena, fica registrada.
