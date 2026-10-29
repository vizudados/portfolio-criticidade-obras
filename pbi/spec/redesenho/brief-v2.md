# Brief · redesenho v2 do painel Criticidade de Obras (Figma primeiro)

Pedido do Alisson em 06/10/2026, retomado em 07/10/2026. Este documento vale para os quatro agentes de tela
(um por tela, todos Opus 5.5) e para a sessão principal que orquestra. **Leia inteiro antes da primeira chamada.**

## 1. O que o Alisson pediu (literal, por item)

1. **Fonte maior no painel inteiro.** Medir o impacto em cada tela, cartão, tooltip e leitura. É o item que mais mexe
   no desenho.
2. **Cartões superiores mais legíveis**, principalmente os títulos: o versalete pequeno e claro "dói a vista". Os
   cartões podem crescer para cima, até o traço que fica abaixo do cabeçalho.
3. **Tirar "FOLHA 01 · …", "FOLHA 02 · …"** dos cabeçalhos das telas.
4. **Espaçamento.** Os gráficos estão muito colados. Separar os painéis e aproveitar melhor o espaço; linhas
   divisórias discretas em creme se ajudar.
5. **T2 · Análise crítica:** redimensionar os gráficos (quadradinho, cascata, mês a mês, sinais).
6. **Negativos em vermelho**, mesmo que discreto: valores, barras e rótulos negativos.
7. **Faixa de status** (creme = estável, hachura cinza = atenção, preto = crítico) se confundia: equilibrar. Com a
   entrada de cor, rever a legenda e as marcas nas quatro telas, nos tooltips e nas leituras.
8. **Tooltips:** os de lista (obras ou itens) crescem em altura; os de gráfico de colunas crescem em largura.
   **Revisar todos** para colisão de cabeçalho e corte de rodapé. Defeito visto: tooltip de item da T2 ("Contas a
   pagar dos medidos", REDINHA ago/26) — o título longo se sobrepõe ao texto da direita do cabeçalho
   ("ITEM 08 · TABELA ANEXADA B106:E114").
9. **Manter** o desenho e a tipografia atuais (Barlow + Segoe UI, paleta do projeto de base), **mas pôr mais cor**.

## 2. Onde trabalhar (Figma)

- Arquivo `FjBWDk5odF9HaZ2pwhGosl`, página **`04 · Redesenho v2 · Painel Criticidade de Obras`** (`372:685`). MCP
  `figma-conta2` (carregar com ToolSearch: `select:mcp__figma-conta2__use_figma,mcp__figma-conta2__get_screenshot,mcp__figma-conta2__get_metadata`).
- Página v1 (`03 · Mockup · Painel Criticidade de Obras`, `269:685`) é **só leitura**: pode ler e clonar dela, nunca alterar.
- Cada agente escreve **só dentro da sua seção** e nunca altera os componentes compartilhados (§3). Precisa mudar
  algo compartilhado? Não mude: descreva no relatório final o que e por quê.

| Tela | Seção v2 (faixa vertical) | Componente v1 | Interações v1 (seção) | Spec v1 |
|---|---|---|---|---|
| T1 · Visão geral (+ drawer de filtros) | `379:788` (y 2500–6700) | `281:720` · filtros abertos `281:724` | `290:720` | `docs/06-interacoes-spec.md` |
| T2 · Análise crítica | `379:789` (y 6900–11100) | `281:721` | `303:2769` | `docs/06-interacoes-spec-t2.md` |
| T3 · Avanço físico | `379:790` (y 11300–15500) | `281:722` | `306:3530` (+ `350:15561` janela/sem previsto) | `docs/06-interacoes-spec-t3.md` |
| T4 · Resultado no tempo | `379:791` (y 15700–19900) | `281:723` | `304:3105` (+ `350:7993` janela) | `docs/06-interacoes-spec-t4.md` |

A seção pode crescer para a direita à vontade; na altura, fique dentro da sua faixa (≤ 4200).

## 3. O sistema v2 (pronto, compartilhado — não alterar)

Quadro **`Sistema v2`** (`373:685`) mostra tudo abaixo. Use **só** estes estilos e variáveis.

**Variáveis** (coleção `Construtora · Painel v2`, modo `Claro` `372:0`):

| Token | Hex | Uso |
|---|---|---|
| base/preto `VariableID:372:687` | #0B0B0C | texto principal, executado/realizado, cartão escuro |
| base/grafite `…:688` | #3B3B3F | texto secundário |
| base/creme `…:689` | #E9E0CF | previsto, verso, pílula ativa |
| base/offwhite `…:690` | #F7F4EE | tooltip, leitura, guia, fundo da tela |
| base/branco `…:691` | #FFFFFF | prancheta |
| texto/terciario `…:692` | #6B6B70 | eixo, nota |
| linha/divisor `…:693` | #E9E0CF | **divisória creme entre painéis** |
| linha/regra `…:694` | #E1E1E1 | regras de tabela e traços do cabeçalho |
| linha/trilha `…:695` | #EFEFEF | trilho de barra |
| status/critico `…:696` · critico-claro `…:697` | #C43737 · #F7E3E3 | crítico (sólido) · fundo de linha em destaque |
| status/atencao `…:698` · atencao-claro `…:699` · atencao-texto `…:700` | #C9821F · #F6E7CF · #8A5A0B | atenção (sólido, texto preto por cima) |
| status/estavel `…:701` · estavel-claro `…:702` · estavel-texto `…:703` · estavel-borda `…:704` | #A9CDB9 · #E1EFE7 · #1E5C43 · #6E9F85 | estável (claro, recua) |
| valor/negativo `…:705` | #C43737 | número, barra e rótulo negativos |
| valor/negativo-sobre-creme `…:706` | #A82C2C | negativo sobre creme (verso) |
| valor/negativo-sobre-preto `…:707` | #F2877C | negativo sobre preto (cartão escuro, cabeçalho de tooltip) |

Ligar pintura: base = valor resolvido da variável, depois `setBoundVariableForPaint` (L017). Transparência vem de
`node.opacity`, nunca da pintura ligada (L008, L012).

**Estilos de texto** (`v2/…`, aplicar com `setTextStyleIdAsync`; IDs no `ledger-figma.json`):

| Estilo | Fonte | Uso | v1 |
|---|---|---|---|
| Página · título | Barlow SB 38/44 | título da tela | 34 |
| Pergunta | Segoe 19/24 | pergunta ao lado do título | 17 |
| Filtro · valor | Barlow SB 19/24 | valor do filtro em uso | 17 |
| Cartão · rótulo | Barlow SB 15/18, caixa normal | **título do cartão** | versalete 10 a 70 % |
| Cartão · número | Barlow SB 42/50 | número do cartão | 38 |
| Cartão · lado | Barlow Medium 17/21 | ao lado do número | 15 |
| Painel · título | Barlow SB 23/28 | título do painel | 20 |
| Subtítulo | Segoe 15/20 | subtítulo do painel | 12–13 |
| Destaque · nome | Barlow SB 21/26 | nome da obra na lista, título do tooltip | 18–19 |
| Valor | Barlow SB 16/20 | valor em linha/tabela | 14,5 |
| Valor · gráfico | Barlow SB 14/17 | rótulo de dado no gráfico | 10–11 |
| Texto | Segoe 15/21 | corpo, detalhe de linha | 13 |
| Texto · forte | Segoe SB 15/21 | rótulo de linha | 13–13,5 |
| Texto · apoio | Segoe 14/19 | contexto do cartão, nota | 13 |
| Eixo | Segoe 13/16 | rótulos de eixo e mês (**único Segoe abaixo de 14**) | 10–11 |
| Chip | Barlow SB 13, 8 %, caixa alta | chips | 11 |
| Versalete | Barlow SB 12, 10 %, caixa alta | cabeçalho de coluna, micro-rótulo (**piso geral 12**) | 9–10,5 |
| Leitura | Segoe 17/26 | texto da leitura e do guia | 15–17 |
| Achado | Barlow SB 34/40 | número de destaque na leitura | 30 |
| Sidebar · item / ativo | Segoe 17/22 | sidebar | 15,5 |

**Componentes compartilhados:**
- `Sidebar · v2` (`376:15025`): variantes `Página=Visão geral | Análise crítica | Avanço físico | Resultado no tempo`.
- `Cartão · v2` (`377:726`): `Tom=Claro | Escuro`, 302 × 140, propriedades de texto `rótulo#377:0`, `número#377:3`,
  `lado#377:6`, `contexto#377:9`. Negativo: trocar o fill do texto `número`/`lado` da instância para
  `valor/negativo` (claro) ou `valor/negativo-sobre-preto` (escuro). `lado` vazio → `visible = false`. A linha
  número + lado tem **262 px** úteis: meça; se passar, o lado vai para a linha de contexto.
- `Ajuda · v2` (`377:727`): "?" de 26 × 26 no canto superior direito de cada painel.
- `Chip · v2` (`373:747`), `Marca · v2` (`373:734`) com `Status=Crítico | Atenção | Estável | Mobilização`.
- `Hachura · v2` (`373:752`) `Sinal=Positivo | Negativo` — receita da trama na descrição do componente (L015, L032).
- **`Casca v2 · modelo`** (`377:10485`): tela 1920 × 1080 pronta com sidebar, prancheta, cabeçalho sem FOLHA,
  linha de 5 cartões e um exemplo de painéis com divisória creme. **Comece a sua tela clonando este frame** para a
  sua seção, troque a variante da sidebar e os textos do cabeçalho/cartões, apague os painéis de exemplo e
  converta em componente (`figma.createComponentFromNode`).

## 4. Grade v2 (coordenadas da prancheta, que fica em x 300, y 12 da tela)

- Conteúdo de x 52 a 1560 (1508 de largura).
- Cabeçalho: título + pergunta pela linha de base em (52, 26); filtro em uso + botões 44 × 44 à direita (y 26).
  **Sem "FOLHA 0X".** Traço `linha/regra` em y 96.
- Cartões: y 97 a 237 (140 de altura), x 52 · 354 · 655 · 957 · 1258; traço em y 237; traços verticais entre
  cartões claros vizinhos (x 957 e 1258 na T1, y 113–221).
- Painéis: de y 261 a y 1028 (767 de altura útil). **Vão de 40 px entre painéis**, com divisória `linha/divisor`
  de 1 px no meio do vão (vertical e horizontal). Nada encosta em nada.
- Cabeçalho de painel: título (Painel · título) em y 0, subtítulo (Subtítulo) em y 32, conteúdo a partir de y 68;
  "?" (`Ajuda · v2`) em (largura − 26, 1).
- A grade é ponto de partida: pode redistribuir larguras/alturas dos painéis da sua tela para caber a fonte maior e
  dar respiro, desde que mantenha cabeçalho, cartões, vão de 40 e divisórias.

## 5. Regras de cor e marca

- **Status por cor e peso**, igual em chip, marca, barra de pontos, colunas por status, tooltips e leituras:
  crítico **vermelho sólido** > atenção **ocre sólido** > estável **sálvia clara** > mobilização **tracejado
  grafite**. Use os componentes `Chip · v2` e `Marca · v2`.
- **Hachura deixou de ser status.** Fica só para a série "sem estoque e adiantamentos": preta quando ≥ 0, vermelha
  quando < 0 (`Hachura · v2`).
- **Negativo em vermelho** (`valor/negativo`): número, sinal, barra e rótulo. Positivo segue preto. Sobre preto,
  `negativo-sobre-preto`; sobre creme, `negativo-sobre-creme`.
- Previsto segue **creme**; executado/realizado segue **preto**; linha de previsto tracejada continua.
- Barras negativas em vermelho (sólido para resultado, hachura vermelha para sem estoque); na cascata da T2, os
  degraus que subtraem (contas a pagar, desembolsado) e um resultado negativo em vermelho.
- Linha da obra crítica em destaque: fundo `status/critico-claro` (no lugar do creme da v1).
- Legendas passam a mostrar as marcas novas; nenhuma legenda pode descrever o código antigo (preto/hachura/creme).

## 6. Tooltips, versos, leituras e guia

- **Tooltip:** corpo **branco** (pedido do Alisson em 07/10; era offwhite), contorno 1 px preto, cantos retos, sombra;
  cabeçalho preto, sem meta de "N obras com aba · X sem planilha". **Lista cresce em altura**
  (até 10 linhas + "e mais N obras"); **gráfico de colunas cresce em largura** (colunas e rótulos com a fonte nova).
  **Cabeçalho:** título longo nunca divide a linha com a meta da direita — quando não cabem lado a lado com 24 px de
  folga, a meta desce para uma 2ª linha do cabeçalho (o cabeçalho cresce). **Rodapé:** caixa de altura fixa presa
  ao pé (L019), uma linha ≤ 70 caracteres; nada cortado. Conferir todos os estados (completo, parcial, vazio,
  mobilização, primeiro mês…).
- **Verso** (flip do cartão): creme, mesmo 302 × 140 do cartão v2, com a escala nova (versalete 12, Segoe 14/15);
  ver anatomia na spec v1 §1.5 e reajustar.
- **Leitura do "?":** cobre **exatamente o retângulo do painel v2** que explica (L065), sem véu; painel pequeno
  recebe versão condensada sem rolagem; **nenhum número repetido** dentro de uma leitura (L058); estilos Leitura e
  Achado.
- **Guia** ("?" redondo do cabeçalho): única peça que cobre a tela inteira (véu 55 %).

## 7. Conteúdo e números

- Dados **reais de ago/26** (6 obras: CAJUEIRO, DUNAS, POTENGI, JANGADA, REDINHA, TIROL; PONTA NEGRA saiu). Sem selo
  `ILUSTR.` (as seis são reais).
- Fonte dos números, nesta ordem:
  1. fotos do Power BI com dados reais: `pbi/qa/desktop/janela-t1.png` … `janela-t4.png` (Desktop a 54 %; dá para
     ler na resolução cheia, 2584 × 1540);
  2. renders 1:1 do HTML com dados reais em `pbi/qa/medidas/` — T1: `janela/` (`t1-ago-j12.png`,
     `t1-drawer-ago-j12.png`, `tt-obra-ago-j12.png`, `tt-mes-ago.png`, `tt-real-t1-ind-*`, `lei-meses-ago-j12.png`…);
     T2: `t2/` (`t2-tela-redinha-j12-2608.png`, `tt-*-redinha-j12-2608.png`, `t2-leituras-*-2608.png`…);
     T3: `t3-final-ago-*.png`, `t3-tt-*.png`, `t3-lei-*.png`, `t3-guia.png`; T4: `t4j-*-ago*.png`, `t4-tt-*`,
     `t4-lei-*`, `t4j-leitura-*-ago*`.
  3. Se algum número não estiver em nenhuma foto, mantenha o da v1 e marque o texto com o sufixo de nome de camada
     `· exemplo` (não invente valor).
- Regras de texto que continuam valendo: janela de 1 a 12 meses nas séries (mostre a de 12, jan–ago/26 = 8 meses);
  obra sem previsto = "sem previsto"; sinal "−" (U+2212) antes do "R$"; números no padrão de
  `pbi/scripts/desenho_projeto.py`.

## 8. Entregas de cada agente (dentro da sua seção)

1. `Tela 0N · v2` — COMPONENTE 1920 × 1080 (T1 também `Tela 01 · v2 · Filtros abertos`, com o drawer: mês, janela
   12/9/6/3, obras, atalhos de status — com a fonte nova).
2. Versos v2 de todos os cartões da tela.
3. Todos os tooltips da tela em v2, com todos os estados.
4. Todas as leituras v2 (na geometria v2 do painel) e o `Guia · T0N · v2`.
5. Fileiras organizadas como na v1 (tela e exemplos · versos · tooltips · leituras e guia), cada fileira com um
   rótulo versalete.
6. Arquivo **`pbi/spec/redesenho/t0N.md`** (no repositório) com: geometria de cada painel/cartão/tooltip/leitura
   v2 (x, y, w, h no canvas 1920 × 1080); **impacto da fonte maior** (tabela elemento × v1 → v2 × o que precisou
   mudar: altura, quebra, truncamento, linhas a menos); cores aplicadas; tudo o que o gerador do Power BI
   (`pbi/scripts/desenho_tN.py`, `tooltips_tN.py`, `leituras_tN.py`, `desenho_comum.py`, casca) vai precisar mudar;
   pendências e dúvidas para o Alisson.
7. Capturas finais (`get_screenshot`) salvas em `pbi/qa/redesenho/t0N-*.png`.

## 9. Como trabalhar (contrato)

- Carregue a skill `vizu-figma` (Skill tool) e as referências `figma-use` e `figma-generate-design` (MCP resources
  `skill://figma/figma-use/SKILL.md` e `skill://figma/figma-generate-design/SKILL.md`) antes do primeiro `use_figma`.
  Passe `skillNames: "resource:figma-use,resource:figma-generate-design,vizu-figma"`.
- Leia as regras aprendidas da skill `vizu-figma` (`references/learned-rules.md`) (L008, L012,
  L015, L017, L019, L021, L022, L023, L032, L034 caem direto aqui) e o checklist `references/qa-gates.md`.
- Só MCP do Figma. Nada de navegador nem Figma Desktop por automação.
- Inspecione antes de escrever; lotes pequenos e retomáveis; devolva todos os IDs criados/alterados; releia e
  capture depois de cada composição. Trabalhe só na sua seção; mais três agentes estão escrevendo no mesmo arquivo,
  cada um na sua faixa — nunca mexa fora dela, nem na v1.
- `toLocaleString('pt-BR')` não funciona no sandbox (L034): formate número à mão.
- Todo texto com um estilo `v2/…`; toda cor de uma variável `Construtora · Painel v2` (exceto artes/ícones clonados).
- Antes de terminar: (a) varra a sua seção e prove por contagem que todo TEXT tem `textStyleId` v2 e nenhum tem
  fonte < 12; (b) nenhum texto sai da caixa do pai (compare `absoluteRenderBounds`); (c) nenhum cabeçalho de tooltip
  com sobreposição; (d) nenhuma legenda com o código antigo; (e) nenhum negativo em preto.
- Relatório final curto: IDs principais, o que mudou, impacto medido da fonte, o que ficou pendente.
