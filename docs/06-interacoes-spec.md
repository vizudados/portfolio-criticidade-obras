# Interações · especificação (fase 1: linguagem comum + Tela 01)

Escrito pelo Fable 5.1 em 06/10/2026, a partir de `docs/05-brief-interacoes.md`. É o que o Opus usa para gerar as
medidas DAX e o que os agentes da fase 2 (Telas 02–04) seguem para manter uma linguagem só. Tudo o que está aqui
existe no Figma, arquivo `FjBWDk5odF9HaZ2pwhGosl`, página `03 · Mockup · Painel Criticidade de Obras` (`269:685`), seção
**`Interações · Tela 01`** (`290:720`, x 0 · y 2460 · 10180 × 3240).

Números: **só** de `mockup/data/criticidade-obras.json` (caminho de cada um na §7). Formatação pt-BR. Tratamento de
dados citado = Power Query.

---

## 0. O que mudou nas cinco telas

### 0.1 Efetivo fora do painel
Removidos da sidebar o rótulo `ETAPA 2 · A COMBINAR` e o item `nav Efetivo (prévia)`; o bloco "Mês de referência"
(rótulo, `junho de 2026`, linha de contexto) subiu **86 px** (y 572 → 486), mantendo o mesmo respiro que havia
entre a nav e o rótulo da etapa 2. Nós removidos: `271:724/725` (T01) · `272:730/731` (Filtros) · `273:731/732`
(T02) · `277:741/742` (T03) · `279:748/749` (T04). A proposta (`246:685`) usa instâncias: acompanha sozinha.

### 0.2 Blocos nomeados (a casca do Power BI sai destes nomes)
Cada KPI virou um frame `Cartão · <nome>` (coluna inteira: 301,6 × 120, colunas em x 52 · 353,6 · 655,2 · 956,8 ·
1258,4 · 1560 da prancheta) e cada bloco de gráfico um frame `Painel · <nome>` com título e subtítulo dentro. Os
frames não têm fundo nem recorte — só agrupam. O botão redondo do cabeçalho passou a chamar `Ajuda · Guia da
página`.

| Tela | Cartões (ids) | Painéis (id · Ajuda) |
|---|---|---|
| 01 · Visão geral (`281:720`) | Obras em andamento `288:7235` · Resultado da carteira `288:7236` · Físico acumulado `288:7237` · Desembolso do mês `288:7238` · Resultado sem estoque `288:7239` | Obras por criticidade `288:7240` · `288:7241` — O que pesa na carteira `288:7244` · `288:7245` — Como o semestre evoluiu `288:7248` · `288:7249` |
| 01 · Filtros abertos (`281:724`) | `289:720` … `289:724` (mesma ordem) | `289:725` · `289:726` — `289:729` · `289:730` — `289:733` · `289:734` |
| 02 · Análise crítica (`281:721`) | Resultado da obra `289:737` · Mês anterior `289:738` · Sem estoque e adiantamentos `289:739` · Físico acumulado `289:740` · Criticidade `289:741` | O quadradinho `289:742` · `289:743` — Desembolso do mês `289:746` (sem "?": bloco de números, não gráfico) — Como o resultado se forma `289:747` · `289:748` — Resultado da obra, mês a mês `289:751` · `289:752` — Sinais do mês `289:755` · `289:756` |
| 03 · Avanço físico (`281:722`) | Desvio físico acumulado `289:7408` · Executado acumulado `289:7409` · Previsto acumulado `289:7410` · No mês `289:7411` · Término previsto `289:7412` | Curva S `289:7413` · `289:7414` — Linha do tempo das obras `289:7417` · `289:7418` — Ritmo do mês `289:7421` · `289:7422` — Avanço das sete obras `289:7425` · `289:7426` |
| 04 · Resultado no tempo (`281:723`) | Resultado da carteira `289:7875` · Mês anterior `289:7876` · Sem estoque e adiantamentos `289:7877` · Desembolso do mês `289:7878` · Justificativas do mês `289:7879` | Resultado da carteira, mês a mês `289:7880` · `289:7881` — Resultado por obra `289:7884` · `289:7885` — Desembolso da carteira `289:7888` · `289:7889` — Desembolso de jun/26 por obra `289:7892` · `289:7893` |

### 0.3 O "?" de cada painel
`Ajuda · <painel>`: círculo de **22 px**, contorno preto a 30 %, "?" em Barlow SemiBold 12,5 grafite; canto superior
direito do painel (x = largura − 22, y 11), centrado na linha do título. Onde a legenda ocupava o canto (T01 Obras por
criticidade, T03 Curva S) ela recuou 34 px. Cartão de KPI **não** tem "?".

### 0.4 Rodapé fora (pedido do Alisson, 06/10)
Saíram das cinco telas a linha "Fonte e tratamento: planilhas Análise Crítica (uma aba por mês) · consultas Power
Query" e o selo "ILUSTRATIVO: … · REAL: CAJUEIRO" (nós `271:1044/1045`, `272:1056/1057`, `273:1342/1343`,
`277:1300/1301`, `279:1323/1324`). Os selos ILUSTR./REAL de cada obra nas listas continuam.
- **Tela 01 e Filtros abertos:** a síntese ("LEITURA DE JUN/26", `271:1041` / `272:1053`) desceu e cresceu:
  prancheta **x 52 · y 945 · 1508 × 84** (canvas **352 · 957 · 1508 × 84**) — respiro de 20 px sobre a lista e a
  coluna do semestre (que terminam em y 925), margem de 27 px até a borda da prancheta; dentro, rótulo em y 17 e
  texto em y 37.
- **Telas 02–04:** só o rodapé saiu. Os painéis de baixo já terminam em 1004–1016 (prancheta), a 40–52 px da
  borda — a mesma margem dos lados —, por isso a opção foi **abrir a margem**, sem esticar contêiner (nenhum
  painel com "?" mudou de geometria; as leituras das T02–T04 ficam como estão).
- **`PBI · Casca · Criticidade de Obras` → `Casca · T1`** (`298:1068`): mesma mudança — texto do rodapé `298:1426`
  apagado; retângulo da síntese `298:1423` movido e redimensionado para a mesma geometria (y 945, 1508 × 84). Os
  frames `Casca · Drawer T1–T4` não tinham rodapé.
- A proposta (`246:685`) usa instâncias das telas e acompanhou.

### 0.5 Piso tipográfico (só na Tela 01 e no estado Filtros abertos)
45 nós ajustados: Segoe UI 11,5 / 12 / 12,5 → **13** (sublinhas dos cartões e das obras, legenda, "crítico: …",
rótulos de mês); dígitos dentro das colunas do semestre, Barlow SemiBold 12 → **14**. Rodapé "Fonte e tratamento"
(11) e versaletes ficaram como estavam (terciário). Telas 02–04 não foram tocadas nisso — tabelas e eixos apertados
pedem revisão caso a caso na fase 2.

---

## 1. Linguagem comum (vale para as Telas 02–04)

### 1.1 Organização na página
Uma **seção por tela**, abaixo das telas, com quatro fileiras (frames transparentes, título + descrição no topo):

| Fileira (y dentro da seção) | Conteúdo | Posições |
|---|---|---|
| `Fileira · Tela atualizada e exemplos` (60) | instância da tela · 4 exemplos montados | x 0, 2020, 4040, 6060, 8080; y 80; rótulo versalete em y 60 |
| `Fileira · Versos` (1260) | 5 versos + `Base · Verso` | x = i × 361,6; base em 5 × 361,6 + 60 |
| `Fileira · Tooltips` (1500) | tooltips com estados + `Base · Tooltip` | x = i × 540 |
| `Fileira · Leituras e guia` (2040) | leituras (na geometria dos painéis) · guia · `Base · Leitura` · `Base · Guia` | leituras lado a lado com 60 px de gap (T01: x 0, 1089, 1590); guia em 2520; bases em 3360 e 4200 |

Próximas seções: `Interações · Tela 02` em y **5900** (= 2460 + 3240 + 200), e assim por diante (altura da seção +
200). Nada sobreposto às telas. Componentes nomeados `Verso · T2 · <cartão>`, `Tooltip · T2 · <ponto>` (estados como
sufixo: `· mobilização`, `· sem crítico`, `· primeiro mês`, `· vazio`), `Leitura · T2 · <painel>`, `Guia · T2`,
`Exemplo · T2 · <gesto>`.

### 1.2 Paleta e superfícies
Só a paleta do projeto: preto `#0B0B0C` · grafite `#3B3B3F` · creme `#E9E0CF` · offwhite `#F7F4EE` · branco; opacidades
para cinzas (regra 12 %, trilha de barra 6–7 %, texto secundário 70–85 %).

| Peça | Superfície | Por quê |
|---|---|---|
| Verso | **creme**, sem borda, sem raio | é o "avesso" quente do cartão; distingue-se do branco e do cartão preto |
| Tooltip | **offwhite** com borda 1 px preta, **cantos retos (raio 0)**, sombra (0, 8, 24, 18 %); **cabeçalho preto 54 px** reto | ecoa a faixa-síntese; flutua sobre a prancheta branca |
| Leitura | **offwhite**, contorno 1 px `#0B0B0C`, **cantos retos (raio 0)**, sombra (0, 12, 32, 22 %), **na geometria exata do painel** que explica; **sem véu** — o resto da tela segue visível (L065) | a leitura "vira" o painel; o × ocupa o canto onde estava o "?" |
| Guia | **offwhite**, raio 20, sombra (0, 24, 60, 35 %); por trás, **véu preto 55 %** sobre o canvas inteiro | único caso que cobre a tela inteira |

**Marcas de status sobre creme ou offwhite** ganham contorno de 1 px preto a 35 % (senão a marca "estável", creme,
some). Sobre branco, como na tela, sem contorno. O código não muda: crítico preto sólido · atenção hachura 45° ·
estável creme · mobilização tracejado.

### 1.3 Tipografia
| Papel | Fonte | Uso |
|---|---|---|
| Versalete (sobretítulo, rótulo de bloco) | Barlow Medium 10–11, espaçamento 16–18 %, grafite 70 % (creme 65 % sobre preto) | único caso abaixo de 13 px |
| Texto corrido | Segoe UI Regular **13 / 17** (verso, tooltip) · 15 / 22 (leitura "o que explica", guia) · 17 / 26 (leitura "explicação") · 13,5 / 18–19 (leitura "como ler", rótulos de destaque, itens do guia) | nunca abaixo de 13 |
| Rótulo de linha | Segoe UI Semibold 13 (nome do indicador/obra) · 14,5 (item do guia) | |
| Valor | Barlow SemiBold **14,5** (tooltip) · 14 (rótulo de barra) · 28 (destaque) · 30 / 36 (achado da leitura, título do guia) | nunca abaixo de 14 |
| Título de tooltip | Barlow SemiBold 18 branco; código Barlow Medium 12 creme 70 %; selo ao lado | |
| Chips e selos | iguais aos da tela (chip Barlow SemiBold 11 / 10 %; selo Barlow SemiBold 9 / 14 %) | |

### 1.4 Marcas, chips, selos (helpers)
- Marca 9 × 9: crítico = retângulo preto; atenção = frame recortado com vetor de linhas a 45°, espaçamento 3,5 px
  (4 px em barras de 8–12 px, 5 px em colunas), contorno 1 px; estável = creme (+ contorno 35 % fora do branco);
  mobilização = contorno tracejado [2, 2].
- Chip: altura 21 (crítico/estável) ou 23 (atenção/mobilização, com contorno), raio 4, marca 8 px + rótulo.
- Selo: `ILUSTR.` tracejado [2, 2] grafite 50 % · `REAL` sólido grafite com texto branco. Sobre o cabeçalho preto do
  tooltip, o selo usa creme (tracejado creme 60 % / sólido creme com texto preto).

### 1.5 Verso (flip do cartão) — anatomia
301,6 × 120, creme, margens 18 / 14. Linhas, de cima para baixo:
1. `COMO É CALCULADO` (versalete, y 14).
2. **Regra** (Segoe 13 / 17, largura 265,6, y 30): pt-BR de gente, **sem nome de coluna**; até 3 linhas (≈ 120
   caracteres) — ou **2 linhas (≈ 80)** quando houver régua.
3. `DE ONDE VEM` (versalete) + origem (Segoe 13, x 100): célula/aba da planilha ou "Power Query".
4. **Régua** (opcional, só em cartão que é indicador da régua): marcas 9 px + limites em Segoe 13, uma linha,
   começa 24 px abaixo da linha de origem.
Sem chip, sem número: o verso explica, não repete.

### 1.6 Tooltip de página — anatomia (fonte única: `Base · Tooltip` `292:1483`)
Largura **480**, altura só a que a leitura pede, sempre ≤ **420** (T01: obra 370; indicador 355; mês 231–253).
Margem 18. **Cantos retos** (raio 0 no cartão e no cabeçalho). Chips e selos dentro do tooltip ficam como na tela
(raio 4 / 3): são os mesmos objetos da tela, e a coerência com ela vale mais que a coerência interna do cartão.
- Cabeçalho preto 54 px: sobretítulo (`CRITICIDADE · JUN/26 · ABA JUN26`), título (nome do ponto), código, selo;
  à direita, versalete de contexto (`INÍCIO ABR/25 · TÉRMINO AGO/28`, `PESO 20 POR OBRA`, `7 OBRAS COM ABA`).
- Corpo: blocos com versalete + linhas de 25–26 px (marca · rótulo · valor · detalhe em grafite · pontos à
  direita), regra de 12 % entre blocos.
- **Mini gráfico objetivo**: **uma série só**; barras de 40 × até 36 px (36 = 100 pontos); **rótulo direto apenas
  no mês do ponto** (Barlow SemiBold 14, preto) **e no extremo** quando ajuda (mesmo corpo a 70 %); rótulo de mês
  embaixo (13, grafite 60 %; o mês do ponto em Semibold preto); **sem eixo, grade, legenda ou enfeite**.
- **Rodapé**: versalete + **uma linha curta (≤ 70 caracteres, Segoe 13)** com o que mudou / o que falta — ou nada,
  quando repetiria o que o tooltip já mostra.
- **Estados**: completo · parcial (o que falta some e o resto reflui: mês sem aba não tem barra nem valor, só o
  rótulo do mês a 30 %; sem "mês anterior" o bloco "desde…" não existe) · vazio (obra sem sinal: linhas todas
  estáveis, "nenhuma" em itálico onde a lista é vazia, série em zero).
- Não repete o chip de status nem a pontuação em destaque — estão na linha sob o mouse. Os valores dos dois
  sinais que a linha já mostra aparecem na **tabela completa** (ficha dos cinco), porque é a tabela que explica os
  pontos; se o Alisson preferir, a medida DAX pode esvaziar esses dois valores.

### 1.7 Leitura do "?" — anatomia e gramática (L065: a leitura cobre o painel que explica)
**Geometria = o retângulo do contêiner do painel** (`Painel · …` na tela: x, y, w, h no canvas), nem mais nem
menos; o resto da tela segue visível, **sem véu**. Superfície offwhite, contorno 1 px `#0B0B0C`, **cantos retos
(raio 0, igual aos tooltips)**, sombra (0, 12, 32, 22 %). Chips e selos dentro da leitura mantêm o raio da tela
(4 / 3), como nos tooltips. **×** fixo no canto superior direito da própria área (28 px, contorno 30 %, a 14 px
das bordas — onde estava o "?"); **sem pílula "Fechar"**: o × basta e clicar fora também fecha. O conteúdo cabe
sem rolagem (L034); piso de 13 px.

Duas versões, decididas pela largura do painel:
- **Completa** (painel largo, ≥ ~900 px; T01 Obras por criticidade): **duas colunas** — à esquerda sobretítulo,
  achado (Barlow SemiBold 26 / 32, ≤ 2 linhas), explicação (Segoe 16 / 24, grafite), destaques (faixa creme, 3
  colunas: número 30 + rótulo 13,5 / 17) e `O QUE EXPLICA` (14,5 / 21); à direita `DETALHE` (mini gráfico, 13,5)
  e `COMO LER` (13,5 / 20). Divisor vertical de 12 % entre as colunas; margens 28; os espaços entre blocos
  crescem até 14 px extras para preencher a altura.
- **Condensada** (painéis estreitos, ~440 px; T01 O que pesa 441 × 375 e Semestre 441 × 265): **uma coluna**,
  margens 18 — sobretítulo (10,5), achado (Barlow SemiBold 21 / 26, ≤ 2 linhas), explicação curta (13 / 17, 3–4
  linhas), **destaques em linhas** (faixa creme; número Barlow 20 à direita de uma coluna de 92 px + rótulo 13 numa
  linha só). Depois, só o que couber, cortando de baixo para cima: `O QUE EXPLICA` (13 / 17), `DETALHE`,
  `COMO LER`. Achado e destaques entram sempre.

Blocos (ordem e gramática):
1. **Sobretítulo** `LEITURA · <PAINEL> · <RECORTE>`.
2. **Achado**: a frase que responde, **com o número-chave**.
3. **Explicação**: estado, causa e impacto — **sem** os números dos destaques; usa palavras (quatro, cinco das
   sete, três quartos).
4. **Destaques**: três números **novos** (rótulo ≤ 46 caracteres na versão condensada).
5. `O QUE EXPLICA`: o porquê, o que puxa.
6. `DETALHE`: mini gráfico, lista ou linha do tempo — sem repetir os números do achado e dos destaques (por isso
   o gráfico de pontos não tem rótulo de valor).
7. `COMO LER`: a régua e o que o mouse ou o clique fazem no painel.
Regra L058: **cada número aparece uma vez por leitura** — achado leva o número-chave; explicação não repete;
destaques trazem números novos; detalhe não repete nenhum dos anteriores. Os números da régua ("peso 35", "de 50
pontos") moram só em `COMO LER`. Texto factual, sem frase de efeito.

### 1.8 Guia da página — anatomia
Painel de 760 (offwhite, raio 20) sobre véu preto 55 % no canvas inteiro — o único que cobre a tela. Sobretítulo `GUIA DA PÁGINA · FOLHA 0X · <TÍTULO>`, título "Como ler
esta tela" (30), introdução (15 / 22), itens numerados (badge 26 px preto com número offwhite · nome Semibold 14,5 ·
descrição 13,5 / 18: o que mostra **e** o que o mouse ou o clique fazem), bloco `A RÉGUA DE CRITICIDADE` (marcas +
limites em duas linhas), fechar. Sobre a tela, **marcadores numerados** (28 px, preto, contorno offwhite 2 px) nos
blocos; o painel fica à esquerda (x 400) para deixar a coluna da direita e o cabeçalho visíveis.

### 1.9 Exemplos montados
Frame 1920 × 1080 com uma **instância da tela** + as peças por cima: cartão virando (frame recortado na coluna do
cartão: clone da frente deslocado −66 px, instância do verso em +54 px, linha de dobra 1 px a 35 %, cursor); tooltip
(cursor na linha, tooltip em cursor + 16 px); leitura (instância **exatamente sobre o painel**, sem véu); guia (véu +
marcadores + instância).
Cursor = SVG de seta branca com contorno preto 1,5 px.

### 1.10 Bases para copiar
`Base · Verso` `291:1149` · `Base · Tooltip` `292:1483` · `Base · Leitura` `294:1293` · `Base · Guia` `294:1315`.
Têm a anatomia com textos entre colchetes; a fase 2 copia (clone → novo componente) e preenche. `Base · Leitura` é
um exemplo de 600 × 420 da versão em uma coluna — a geometria real é sempre a do painel (§1.7); `Base · Tooltip`
já traz cantos retos, mini gráfico de uma série e rodapé de uma linha. Os scripts desta
fase constroem tudo por código com helpers `T` (texto), `R` (retângulo), `FR` (frame), `HACH` (hachura), `MARK`,
`CHIP`, `SELO`, `COMP` — reproduzir os mesmos parâmetros (§1.2–1.4) garante a consistência.

### 1.11 Como reconstruir no Power BI
| Peça | Visual | Observações |
|---|---|---|
| Verso | **HTML Content** (frente e verso no mesmo visual, do tamanho da coluna do cartão) | `:hover` e `:focus-within` deslizam a frente para cima e o verso para dentro (transição ~220 ms); sem mouse (toque) o toque alterna. Texto do verso é medida DAX (regra fixa; régua lê `meta.regras_criticidade`). |
| Tooltip | **Página de tooltip** 480 × (altura da peça, ≤ 420) (tipo "Tooltip", tamanho personalizado), fundo offwhite com borda preta e cantos retos, cabeçalho = retângulo preto + medidas; tabela e série em HTML Content ou visuais nativos | o Power BI posiciona a página junto ao cursor; o Figma mostra a 100 %. Estados são a mesma página com medidas que devolvem vazio (`BLANK()` some, zero real = "0"). |
| Leitura | **HTML Content na geometria exata do painel** (mesmo x, y, w, h do contêiner), **aberto por marcador** que só liga esse visual; **× = botão transparente** fixo no canto superior direito da área, com ação de marcador "normal"; um botão transparente do tamanho da página, atrás do painel aberto, fecha ao **clicar fora** | sem véu; marcador com "Dados" desmarcado — não mexe em filtro nem página. Um marcador por painel; "?" = botão com ação. |
| Guia | Marcador com véu + formas (círculos numerados) + HTML Content | único que cobre a tela; o "?" redondo do cabeçalho aciona. |
| "?" dos painéis | Botão de 22 px (forma redonda) com ação de marcador | nome do botão = `Ajuda · <painel>`. |
| **Animação** (o Alisson implementa) | **Contador** nos números: no verso nenhum (texto fixo); no tooltip os valores das linhas e os pontos contam do zero ao abrir; na leitura o número-chave do achado e os três destaques contam. **Barras em estilo racing**: no tooltip a série mensal cresce do zero em sequência, do primeiro mês ao mês do ponto (o mês do ponto por último, e seu rótulo só aparece ao fim); nas listas por obra as barras/pontos entram de cima para baixo; na leitura o gráfico de pontos das obras cresce da maior para a menor, e as linhas tracejadas de 25 e 50 **se desenham** da esquerda para a direita antes das barras. Linhas de série (quando houver, T03–T04) se desenham da esquerda para a direita. O flip do verso é a única animação de layout (deslize ~220 ms). | a ordem é sempre a de leitura: contador → barras → texto. |

Os textos de leitura e tooltip são **dinâmicos** (mudam com mês, obra e filtro): a §3–4 traz o modelo de cada
frase com as variações; a §7 lista o que o JSON já tem e o que falta.

---

## 2. Versos · Tela 01

Gatilho: hover (ou foco) no cartão. Sem estados — o texto é fixo; só a régua lê `meta.regras_criticidade`.

| Componente · id | Cartão (id) | Regra (sobretítulo `COMO É CALCULADO`) | `DE ONDE VEM` | Régua | Campos JSON |
|---|---|---|---|---|---|
| `Verso · T1 · Obras em andamento` `291:1094` | `288:7235` | Obras com aba do mês na Análise Crítica. O valor soma o orçamento projetado; a linha de baixo conta os status. | J28 de cada aba · Power Query | — | `carteira.obras_em_andamento`, `.orcamento`, `.criticas/.atencao/.estaveis` |
| `Verso · T1 · Resultado da carteira` `291:1099` | `288:7236` | Soma do resultado das 7 obras: crédito do executado + pago não aplicado − gasto. | D155 e E155 da aba do mês | ■ < 0 · ▨ 0 a +1,0% · □ ≥ +1,0% | `carteira.resultado`, `.resultado_pct`; régua `meta.regras_criticidade.resultado_pct` |
| `Verso · T1 · Físico acumulado` `291:1112` | `288:7237` | Executado e previsto acumulados, ponderados pelo orçamento; desvio em p.p. | F35 e F37 da aba do mês | ■ < −3,0 · ▨ −3,0 a −1,0 · □ ≥ −1,0 p.p. | `carteira.exec_acum_ponderado`, `.prev_acum_ponderado`, `.desvio_fisico_pp`; régua `…desvio_fisico_pp` |
| `Verso · T1 · Desembolso do mês` `291:1125` | `288:7238` | Desembolsado e previsto do mês somados; desvio = desembolsado ÷ previsto − 1. | J136 e J137 da aba do mês | ■ > +25% · ▨ +10% a +25% · □ ≤ +10% | `carteira.desembolsado_mes_rs`, `.previsto_mes_rs`, `.desvio_desembolso`; régua `…desvio_desembolso` |
| `Verso · T1 · Resultado sem estoque` `291:1138` | `288:7239` | Resultado menos o que foi pago e ainda não virou obra: estoque e adiantamentos. | D155 − D146 a D150 da aba | ▨ < 0 atenção · □ ≥ 0 estável | `carteira.resultado_sem_ativos`, `.ativos_nao_consumidos`; régua `…resultado_sem_ativos` |

Nas Telas 02–04 o "7 obras" vira "da obra" quando o cartão é de uma obra; a régua entra em todo cartão que seja
indicador (resultado %, desvio físico, desembolso, variação, sem estoque) e sai dos demais (mês anterior, término,
justificativas).

---

## 3. Tooltips · Tela 01

### 3.1 `Tooltip · T1 · Obra` (`292:1094`) — estados `· mobilização` (`292:1157`) e `· estável` (`292:1218`)
**Gatilho:** hover numa linha de "Obras por criticidade" (`288:7240`). **Ponto:** a obra. **480 × 370** (os três
estados). Cantos retos; chips/selos como na tela.

| Bloco | Modelo (jun/26, REDINHA) | Variações | Campos |
|---|---|---|---|
| Sobretítulo | `CRITICIDADE · {MÊS} · ABA {aba}` | `+ · EM MOBILIZAÇÃO` quando `mobilizacao` | `ultimo.mes`, `ultimo.aba`, `ultimo.mobilizacao` |
| Título | `REDINHA` `AT` `ILUSTR.` | selo `REAL` quando `fonte = "real"` | `obra`, `codigo`, `fonte` |
| Contexto (direita) | `INÍCIO ABR/25 · TÉRMINO AGO/28` | — | `inicio`, `termino_previsto` |
| `SINAIS E PONTOS` · `PONTOS · PESO` | 5 linhas, ordem = `sinais` (status desc, peso desc), depois os estáveis por peso: marca · nome curto · valor · detalhe · `pontos / peso` | nome curto: Físico acumulado · Desembolso do mês · Resultado · Variação no mês · Sem estoque. Detalhe por indicador: físico `{exec_acum} × {prev_acum} previsto`; desembolso `{desembolsado} × {previsto}`; resultado `{resultado R$} · maio {resultado_pct_mes_anterior}`; variação `cai desde {mês}` / `sobe desde {mês}` (primeiro mês da sequência de mesmo sinal na `serie`; se só 1 mês: `era {valor} em {mês}`); sem estoque `{ativos} não aplicados` | `ultimo.indicadores`, `ultimo.indicadores_status`, `meta.regras_criticidade.*.peso`, `ultimo.resultado_pct_mes_anterior`, `serie[].indicadores.variacao_resultado_pp` |
| `PONTOS, MÊS A MÊS` | 6 barras jan–jun (40 × até 36 px) com status (creme/hachura/preto); **rótulo de valor só no mês do ponto** (jun, Barlow 14 preto) **e no extremo** (mín. para obra que piora, máx. para obra que melhora; a 70 %); mês embaixo, o do ponto em Semibold; sem eixo nem grade | mês sem aba: sem barra e sem valor, rótulo a 30 % (TIROL jan/fev); série toda igual: só o rótulo do ponto; obra estável: barras em zero, rótulo "0" no ponto e o extremo (DUNAS jan "5") | `serie[].score`, `serie[].status` |
| `DESDE {MÊS ANTERIOR}` (rodapé, **uma linha ≤ 70**) | "físico: atenção → crítico (era −2,9 p.p.) · variação: entrou em atenção" | `{indicador curto}: {status anterior} → {status} (era {valor anterior})` por indicador que mudou, separados por " · "; `{indicador}: entrou em {status}` quando vinha de estável; se nada mudou: "nada mudou: os cinco indicadores seguem estáveis"; mais de dois indicadores mudaram: "{n} sinais mudaram de faixa: {lista curta}"; primeiro mês do histórico: rodapé some. Mobilização: título `DESDE MAIO · TRAVA DA MOBILIZAÇÃO` + "físico: estável → atenção · em mobilização, pontuação travada em 49" | `serie[-2].indicadores_status` × `ultimo.indicadores_status`, `serie[-2].indicadores`, `ultimo.mobilizacao` |

Textos montados nos três estados (todos no Figma):
- REDINHA (completo): linhas `■ Físico acumulado −3,9 p.p. · 24,1% × 28,0% previsto · 25 / 25` · `■ Desembolso do mês +36% · R$ 638 mil × R$ 469 mil · 20 / 20` · `▨ Resultado +0,40% · R$ 90 mil · maio +0,72% · 17,5 / 35` · `▨ Variação no mês −0,32 p.p. · cai desde abril · 5 / 10` · `▨ Sem estoque −R$ 721 mil · R$ 811 mil não aplicados · 5 / 10`; série 15 · 32,5 · 45 · 55 · 55 · 72,5 (rótulos só em jan "15" e jun "72,5"); rodapé `DESDE MAIO` "físico: atenção → crítico (era −2,9 p.p.) · variação: entrou em atenção".
- TIROL (parcial): `■ Resultado −0,90% · −R$ 231 mil · maio −0,65% · 35 / 35` · `■ Desembolso do mês +39% · R$ 463 mil × R$ 333 mil · 20 / 20` · `▨ Físico acumulado −1,4 p.p. · 3,6% × 5,0% previsto · 12,5 / 25` · `▨ Variação no mês −0,25 p.p. · cai desde abril · 5 / 10` · `▨ Sem estoque −R$ 268 mil · R$ 37 mil não aplicados · 5 / 10`; série — · — · 49 · 49 · 49 · 49 (rótulo só em jun); rodapé `DESDE MAIO · TRAVA DA MOBILIZAÇÃO` "físico: estável → atenção · em mobilização, pontuação travada em 49" (o "somaria 77,5" saiu — a coluna de pontos permite somar).
- DUNAS (vazio): cinco linhas estáveis (`+2,30% · R$ 600 mil · maio +2,26% · 0 / 35`, `+1,1 p.p. · 56,1% × 55,0% previsto · 0 / 25`, `−4% · R$ 1,67 mi × R$ 1,73 mi · 0 / 20`, `+0,04 p.p. · sobe desde fevereiro · 0 / 10`, `+R$ 100 mil · R$ 500 mil não aplicados · 0 / 10`); série 5 · 0 · 0 · 0 · 0 · 0 (rótulos em jan "5" e jun "0"); rodapé "nada mudou: os cinco indicadores seguem estáveis".

### 3.2 `Tooltip · T1 · Indicador` (`292:1276`) — estado `· sem crítico` (`292:1345`)
**Gatilho:** hover numa barra de "O que pesa na carteira" (`288:7244`). **Ponto:** o indicador. **480 × 355** (os
dois estados). Sem mini gráfico (a lista por obra é o gráfico).

| Bloco | Modelo (Desembolso do mês × previsto) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `O QUE PESA NA CARTEIRA · JUN/26` · título = rótulo do indicador · `PESO {peso} POR OBRA` | — | `carteira.indicadores[].rotulo`, `.peso` |
| Faixa | `■ > +25% crítico · ▨ +10% a +25% atenção · □ ≤ +10% estável` | indicador sem faixa crítica: `▨ < 0 atenção · □ ≥ 0 estável · nunca crítico sozinho` (texto cinza) | `meta.regras_criticidade[ind].{critico,atencao,estavel}` |
| `OBRA POR OBRA` · `PONTOS` | 7 linhas ordenadas do pior ao melhor valor: marca · obra + selo · valor · detalhe · pontos | detalhe por indicador: desembolso `{desembolsado} × {previsto}`; sem estoque `{ativos} não aplicados`; resultado `{resultado R$}`; físico `{exec} × {prev} previsto`; variação `era {resultado_pct anterior}` | `obras[].ultimo.indicadores[ind]`, `.indicadores_status[ind]`, `obras[].fonte` |
| Rodapé (**uma linha ≤ 70**) | `JUSTIFICATIVA NA PLANILHA`: "exigida acima de ±10%: {preenchidas} de {exigidas} preenchidas · {obra} em branco" | só no desembolso; sem ausentes: "exigida acima de ±10%: todas preenchidas"; nos outros indicadores `COMO LER` com uma linha (sem estoque: "soma no resultado o que foi pago e ainda não virou obra"), ou nada se a faixa já explica | `carteira.justificativas_exigidas`, `.justificativas_preenchidas`, `.justificativas_ausentes` |

### 3.3 `Tooltip · T1 · Mês` (`292:1416`) — estado `· primeiro mês` (`292:1451`)
**Gatilho:** hover numa coluna de "Como o semestre evoluiu" (`288:7248`). **Ponto:** o mês. **480 × 231** (jun) /
**253** (jan).

| Bloco | Modelo (junho) | Variações | Campos |
|---|---|---|---|
| Cabeçalho | `COMO O SEMESTRE EVOLUIU · JUN/26` · "junho de 2026" · `7 OBRAS COM ABA` | primeiro mês: `· PRIMEIRO MÊS DO HISTÓRICO` e `6 OBRAS COM ABA · TIROL SEM PLANILHA` | `carteira.serie[].obras`; obras sem `serie[mes]` |
| Três colunas | chip CRÍTICO / ATENÇÃO / ESTÁVEL, obras do status naquele mês com pontos (marca tracejada antes da obra em mobilização) | coluna vazia: "nenhuma" em itálico | `obras[].serie[mes].status/.score/.mobilizacao` |
| Rodapé (**uma linha ≤ 70**) — `DESDE {MÊS ANTERIOR}` | "JANGADA saiu de crítico (desembolso +53% → +15%) · nenhuma obra entrou" | `{obra} entrou em crítico ({indicador} {de} → {para})` / `{obra} saiu de crítico (…)`; `nenhuma obra entrou` / `nenhuma saiu`; mais de duas mudanças: "{n} obras mudaram de faixa: {lista}"; nada mudou: "mesmos status de {mês anterior}" | `obras[].serie[m−1].status` × `serie[m].status` e o indicador que mudou de faixa |
| Rodapé alternativo — `CARTEIRA NO MÊS` | só quando **não há mês anterior** (primeiro mês): "resultado R$ 1,58 mi (+1,16%) · desembolso +12% sobre o previsto" | nos demais meses a linha sai: repetiria os cartões (mês do filtro) ou alongaria o tooltip | `carteira.serie[].resultado/.resultado_pct/.desvio_desembolso` |

---

## 4. Leituras · Tela 01

Geometria (canvas 1920 × 1080): a leitura ocupa o contêiner do painel — **Obras por criticidade x 352 · y 282 ·
1029 × 655** (versão completa, duas colunas) · **O que pesa na carteira x 1420 · y 282 · 441 × 375** (condensada) ·
**Como o semestre evoluiu x 1420 · y 672 · 441 × 265** (condensada). Os textos abaixo são os que estão no Figma;
onde a versão condensada encurtou, a "versão longa" fica registrada para painéis largos de outras telas.

### 4.1 `Leitura · T1 · Obras por criticidade` (`294:1094`, 1029 × 655 em (352, 282)) — "?" `288:7241`
Versão **completa**, duas colunas (esquerda: sobretítulo, achado 26, explicação 16/24, destaques, o que explica;
direita: detalhe + como ler). Nada saiu; só a pílula "Fechar" (o × fica no canto).
| Bloco | Texto (jun/26) | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · OBRAS POR CRITICIDADE · JUNHO DE 2026` | mês por extenso | `carteira.mes_ref` |
| Achado | "2 obras críticas em junho: REDINHA e POTENGI. Outras 3 pedem atenção e 2 seguem estáveis." | `{n} obra(s) crítica(s) em {mês}: {lista}. Outras {a} pedem atenção e {e} seguem estáveis.` · zero críticas: `Nenhuma obra crítica em {mês}: {a} em atenção e {e} estáveis.` · uma só: `Uma obra crítica em {mês}: {obra}.` | `carteira.criticas/.atencao/.estaveis`, `obras[].ultimo.status` |
| Explicação | "REDINHA entrou em crítico pelo ritmo: o físico ficou atrás do cronograma e o desembolso do mês passou do previsto, com um resultado que só é positivo por causa do estoque. POTENGI é crítica pelo resultado, negativo e piorando com três quartos da obra executados. Juntas, as duas puxam para baixo um resultado de carteira que cai desde janeiro." | uma frase por obra crítica, montada pelo sinal crítico de maior peso: físico → "entrou em crítico pelo ritmo: o físico ficou atrás do cronograma"; desembolso → "e o desembolso do mês passou do previsto"; resultado → "é crítica pelo resultado, negativo e piorando" (+ "com {fração} da obra executados" a partir de `exec_acum`: um quarto / metade / três quartos); sem estoque em atenção → "com um resultado que só é positivo por causa do estoque". Fecho: "Juntas, as {n} puxam para baixo um resultado de carteira que {cai desde {mês} / subiu em {mês}}" (sinal da `carteira.serie[].resultado`). Sem obra crítica: "Nenhuma obra está fora da faixa crítica; o que pede atenção é {indicador mais frequente}." | `obras[].ultimo.sinais`, `.exec_acum`, `carteira.serie[].resultado` |
| Destaques | `72,5` pontos da REDINHA, a obra mais crítica da carteira · `−1,60%` resultado da POTENGI sobre o orçamento (−R$ 354 mil) · `R$ 361 mil` queda do resultado da carteira em relação a maio | 1: `score` da 1.ª obra; 2: o valor do sinal crítico de maior peso da 2.ª obra (ou, com uma só crítica, o 2.º sinal da 1.ª); 3: `variacao_resultado` da carteira ("queda" / "alta") | `obras[0].ultimo.score`, `obras[1].ultimo.indicadores`, `carteira.variacao_resultado` |
| O que explica | "Os dois sinais com mais peso na régua — resultado da obra e desvio físico — estão fora da faixa em quatro obras cada; o desembolso do mês acima do previsto aparece em cinco das sete. Nas estáveis, DUNAS e PONTA NEGRA, nenhum indicador saiu da faixa." | contagens em palavras a partir de `carteira.indicadores[].criticas + atencao`; última frase lista as estáveis (ou "Nenhuma obra está estável.") | `carteira.indicadores[]` |
| Detalhe | barras de pontos das 7 obras (status na cor), linhas tracejadas em 25 e 50 com rótulos "25 · atenção" e "50 · crítico"; **sem rótulo de valor** (L058) | ordem = a da tela | `obras[].ultimo.score/.status` |
| Como ler | "Cada obra soma pontos em cinco indicadores — resultado da obra (peso 35), desvio físico (25), desembolso do mês (20), variação do resultado (10) e resultado sem estoque (10). Crítico vale o peso inteiro; atenção, a metade. De 50 pontos a obra é crítica; de 25 a 49, atenção; abaixo, estável. Com menos de 10% executado a obra está em mobilização e fica, no máximo, em atenção." | fixo; lê `meta` | `meta.regras_criticidade`, `meta.limites` |

### 4.2 `Leitura · T1 · O que pesa na carteira` (`294:1144`, 441 × 375 em (1420, 282)) — "?" `288:7245`
Versão **condensada**: sobretítulo, achado (21/26), explicação (13/17, 4 linhas), destaques em linhas, `O QUE
EXPLICA`. **Saíram:** `DETALHE` (a tabela de quem está fora da faixa — o tooltip do indicador a cobre) e `COMO LER`.
| Bloco | Texto (condensado, no Figma) | Modelo e variações | Campos |
|---|---|---|---|
| Achado | "Desembolso acima do previsto: o sinal mais espalhado, em 5 das 7 obras." | `{indicador}: o sinal mais espalhado, em {n} das {total} obras.` · empate: "{A} e {B} empatam: {n} das {total} obras fora da faixa." · versão longa: "O desembolso acima do previsto é o sinal mais espalhado: 5 das 7 obras fora da faixa." | `carteira.indicadores[].criticas/.atencao`, `carteira.obras_em_andamento` |
| Explicação | "Em pontos, o resultado da obra pesa mais (maior peso, duas obras com prejuízo). Mas é o desembolso que atravessa a carteira: três obras gastaram mais de um quarto acima do previsto, a maior delas, a CAJUEIRO, sem justificativa na planilha." | 1.ª frase: indicador com mais `pontos_carteira` e o porquê (peso + nº de críticas em palavras); 2.ª: o mais espalhado, com as críticas descritas pela faixa ("mais de um quarto acima" = `> +25%`) e a obra de maior desvio + `justificativa_ausente`. Versão longa acrescenta: "O desvio físico vem em seguida, com uma obra crítica e três em atenção." | `carteira.indicadores[]`, `obras[].ultimo.justificativa_ausente` |
| Destaques (linhas) | `105 pts` indicador com mais pontos: resultado da obra · `+58%` desembolso da CAJUEIRO, o maior desvio do mês · `4 de 5` justificativas preenchidas entre as exigidas | 1: maior `pontos_carteira`; 2: maior `desvio_desembolso` entre as obras; 3: `justificativas_preenchidas de justificativas_exigidas`; rótulos ≤ 46 caracteres | `carteira.indicadores[].pontos_carteira`, `obras[].ultimo.desvio_desembolso`, `carteira.justificativas_*` |
| O que explica | "O resultado vale 35 pontos por obra e o desembolso 20: por isso o desembolso lidera em obras afetadas, não em pontos. Todas menos DUNAS e PONTA NEGRA ficariam negativas sem estoque e adiantamentos." | pesos de `meta`; "todas menos {estáveis no sem-estoque}" / "{n} obras ficariam negativas" | `meta.regras_criticidade.*.peso`, `carteira.indicadores[resultado_sem_ativos].atencao` |
| Detalhe (só em painel largo) | tabela: indicador · ■ obras críticas · ▨ obras em atenção (5 linhas) | linha sem críticas mostra só a hachura | `carteira.indicadores[].criticas/.atencao` |
| Como ler (só em painel largo) | "Cada barra soma os pontos que o indicador deu às sete obras: o peso inteiro por obra crítica, a metade por obra em atenção. A barra cheia seria todas as obras críticas naquele indicador. Passe o mouse para ver obra por obra." | fixo | — |

### 4.3 `Leitura · T1 · Como o semestre evoluiu` (`294:1196`, 441 × 265 em (1420, 672)) — "?" `288:7249`
Versão **condensada mínima**: sobretítulo, achado (21/26), explicação (13/17, 3 linhas), destaques em linhas.
**Saíram:** `O QUE EXPLICA`, `DETALHE` (a linha do tempo de mudanças — o tooltip do mês cobre "desde o mês
anterior") e `COMO LER`.
| Bloco | Texto (condensado, no Figma) | Modelo e variações | Campos |
|---|---|---|---|
| Sobretítulo | `LEITURA · COMO O SEMESTRE EVOLUIU · JAN A JUN/26` | primeiro e último mês da série | `carteira.serie[0/−1].mes` |
| Achado | "De nenhuma crítica a duas; o resultado foi de R$ 1,58 mi a R$ 731 mil." | `De {críticas no 1.º mês} crítica(s) a {críticas no último}; o resultado foi de {R$ 1.º} a {R$ último}.` · versão longa: "De nenhuma obra crítica a duas no semestre; o resultado caiu de R$ 1,58 mi para R$ 731 mil." | `carteira.serie[0/−1].criticas/.resultado` |
| Explicação | "A piora começou em março (POTENGI, pelo resultado) e se firmou em abril (REDINHA, físico e desembolso). Maio foi o pico; em junho o JANGADA voltou para atenção, mas as duas que restam pesam mais." | frases pelos meses em que `obras[].serie[].status` muda: "{A piora/A melhora} começou em {mês} ({obra}, por {sinal})"; "se firmou em {mês} ({obra}, {sinais})"; "{mês} foi o pico"; "em {mês} {obra} voltou para atenção"; "as que restam pesam mais" só se o `score` das críticas subiu. Versão longa acrescenta: "Desde maio só DUNAS e PONTA NEGRA seguem estáveis — a CAJUEIRO deixou a faixa pelo desembolso." | `obras[].serie[].status/.score/.indicadores_status` |
| Destaques (linhas) | `3` obras críticas em maio, o pico do semestre · `R$ 2,92 mi` pagos e não aplicados (jan.: R$ 1,60 mi) · `−0,5 p.p.` físico ponderado (jan.: +1,3 p.p.) | 1: máx. de `serie[].criticas` e o mês; 2: `ativos_nao_consumidos` último (1.º entre parênteses); 3: `desvio_fisico_pp` último (1.º entre parênteses) | `carteira.serie[]` |
| O que explica (só em painel largo) | "O movimento é de estoque e adiantamentos: o dinheiro pago que ainda não virou obra subiu todo mês, e o resultado sem ele foi negativo nos seis meses. É por isso que o resultado oficial cai mesmo com o físico ponderado perto do previsto." | "subiu todo mês" / "subiu em {n} dos {m} meses"; "negativo nos {m} meses" / "negativo desde {mês}"; "perto do previsto" quando `|desvio_fisico_pp| ≤ 1` | `carteira.serie[].ativos_nao_consumidos/.resultado_sem_ativos/.desvio_fisico_pp` |
| Detalhe (só em painel largo) | linha do tempo em 6 colunas: mês + "o que mudou de status": jan "nenhuma obra crítica" · fev "REDINHA → atenção" · mar "POTENGI → crítica · TIROL abre a planilha" · abr "REDINHA → crítica" · mai "JANGADA → crítica · CAJUEIRO → atenção" · jun "JANGADA → atenção" | `{obra} → {status}` por mudança; `{obra} abre a planilha` quando a série começa; mês sem mudança: "sem mudança" | `obras[].serie[].status` |
| Como ler (só em painel largo) | "Cada coluna conta as obras por status no mês: preto crítico, hachura atenção, creme estável. A soma é o número de obras com aba naquele mês — seis em janeiro e fevereiro, sete desde março, quando a TIROL abriu a planilha. Passe o mouse num mês para ver quem estava em cada faixa." | contagens de `serie[].obras` em palavras | `carteira.serie[].obras` |

---

## 5. `Guia · T1` (`294:1236`, 760 × 858) — "?" `271:742` (`Ajuda · Guia da página`)
Véu 55 % + marcadores numerados + painel em x 400 (centrado na vertical). Texto (fixo, muda só com o mês):
1. **Cartões da carteira** — Cinco números do mês; o escuro é a resposta da pergunta. Passe o mouse: o cartão vira e mostra como é calculado e de onde vem.
2. **Obras por criticidade** — As sete obras em ordem de pontos, com os dois sinais que mais pesam. Passe o mouse numa obra para ver os cinco sinais e a trajetória do semestre.
3. **O que pesa na carteira** — Pontos somados das sete obras, por indicador. Passe o mouse para ver obra por obra.
4. **Como o semestre evoluiu** — Obras por status, mês a mês. Passe o mouse num mês para ver quem estava em cada faixa e o que mudou.
5. **Leitura do mês** — A síntese escrita do mês; muda com o filtro.
6. **Filtro e ajuda** — O topo mostra o recorte em uso. O funil abre os filtros de mês e obra; o "?" redondo abre este guia; o "?" de cada painel abre a leitura daquele gráfico.
7. **Navegação** — Visão geral · Análise crítica · Avanço físico · Resultado no tempo. A obra e o mês escolhidos valem para todas as folhas.
Régua: ■ crítico · 50 pontos ou mais ▨ atenção · 25 a 49 □ estável · abaixo de 25 ⬚ mobilização · menos de 10% executado: a obra fica, no máximo, em atenção. "Os pontos somam cinco indicadores com pesos diferentes; a leitura de cada painel explica a conta e a faixa de cada um."
Marcadores (canvas 1920): 1 (338, 130) cartões · 2 (338, 278) lista · 3 (1408, 278) o que pesa · 4 (1408, 666) semestre · 5 (338, 928) síntese · 6 (1452, 44) filtro/ajuda · 7 (14, 218) navegação.

---

## 6. Exemplos montados (fileira 1)
`Exemplo · T1 · Cartão virando` `295:1094` (frame `flip · meio do gesto` `295:1471`) · `Exemplo · T1 · Tooltip
apontando` `295:1494` · `Exemplo · T1 · Leitura aberta` `295:1936` · `Exemplo · T1 · Guia aberto` `295:2364`.
Instância da tela atualizada: `290:733`.

---

## 7. Números: origem e o que falta no JSON

**Conferidos (caminho no JSON):** `carteira.*` (731 mil, +0,45 %, 361 mil, 45,2/45,7 %, −0,5 p.p., 6,21/5,20 mi,
+19 %, −2,19 mi, 2,92 mi, 2/3/2, justificativas 5/4, CAJUEIRO ausente); `carteira.serie[]` (jan: 1,58 mi, +1,16 %,
5,00/4,47 mi, +12 %, 1,60 mi, −15 mil; críticas 0·0·1·2·3·2; obras 6·6·7·7·7·7; +1,26 → "+1,3 p.p."); `obras[].ultimo`
de cada obra (status, score, indicadores, sinais, resultado_pct_mes_anterior, inicio/termino); `obras[].serie[]`
(scores por mês, status, `desvio_fisico_pp` de maio −2,87 → "−2,9", TIROL maio −0,79 → "−0,8", JANGADA maio
`desvio_desembolso` 0,53 → "+53 %"); `meta.regras_criticidade` e `meta.limites`.

**Derivados pela régua documentada (não existem como campo — acrescentar em `montar_dados_mockup.py`):**
- `pontos_por_indicador` = peso × status ÷ 2 (ex.: REDINHA 25 · 20 · 17,5 · 5 · 5; soma 72,5 = `score`). Usado na
  tabela dos tooltips de obra e na coluna "pontos" dos tooltips de indicador. Sugestão: `ultimo.indicadores_pontos`.
- `score_bruto` antes da trava de mobilização (TIROL 77,5, exibido no tooltip; `score` = 49). Sugestão:
  `ultimo.score_bruto`.
- `mudancas_desde_mes_anterior`: lista `{indicador, de, para}` comparando `serie[−2].indicadores_status` com
  `ultimo.indicadores_status` (hoje a comparação é feita à mão). Idem por obra para "entrou/saiu de crítico".
- Sequências "cai desde abril" / "sobe desde fevereiro" (sinal consecutivo da variação) e "subiu todo mês"
  (ativos) — são comparações de sinal, não contas, mas convém um campo `tendencia` para a DAX não varrer a série.
- Contagens em palavras ("quatro obras cada", "cinco das sete", "três quartos executados" = 74,0 %) — vêm de
  contagens e arredondamento de campos existentes.

**Não usados por falta de campo:** desvio de desembolso da carteira em R$ (só há % — "R$ 1,01 mi" ficou de fora);
`resultado_sem_ativos` por obra no mês anterior (não precisou).

---

## 8. O que fica diferente no Power BI
- O flip é por hover/foco; em toque (celular) vira por clique. O verso ocupa exatamente o visual do cartão (coluna).
- A página de tooltip aparece onde o Power BI decidir perto do cursor (o exemplo mostra uma posição possível); a
  sombra e o raio vêm do fundo da página (retângulo).
- Leitura: HTML Content na geometria do painel, ligado por marcador; o × (botão transparente no canto) e o clique
  fora (botão transparente atrás) voltam ao marcador "normal"; abrir não filtra nada. Guia: idem, com véu.
- **Animação da T1** (o Alisson implementa): tooltip de obra — os cinco valores e os "pontos / peso" contam do
  zero; as barras jan→jun crescem em sequência (racing), a de jun por último, e só então aparecem os rótulos "15"
  e "72,5"; o rodapé entra por último. Tooltip de indicador — as sete linhas entram de cima para baixo com o valor
  e os pontos contando. Tooltip de mês — os pontos de cada obra contam; as três colunas entram crítico → atenção →
  estável. Leitura Obras por criticidade — "2", "3", "2" do achado e os três destaques (72,5 · −1,60% · R$ 361
  mil) contam; no detalhe as linhas tracejadas de 25 e 50 se desenham da esquerda para a direita e depois as sete
  barras crescem da maior para a menor. Leituras condensadas — número-chave e destaques contam, nada mais. Verso —
  só o deslize do flip.
- Os textos das leituras são medidas DAX com as variações da §3–4; onde o texto depende de lista (obras,
  indicadores) usar `CONCATENATEX` com " · " e "e" antes do último.
- Segoe UI e Barlow: Barlow só em número e dentro do HTML Content (as páginas nativas usam Segoe).
- Hachura em HTML = `repeating-linear-gradient(45deg, #0B0B0C 0 1px, transparent 1px 3.5px)` com borda 1 px.

---

## 9. Fase 2 · roteiro para as Telas 02–04
1. Seção `Interações · Tela 0X` em y 5900 (T02), depois +altura+200; fileiras como na §1.1.
2. Instância da tela (já com `Cartão/Painel/Ajuda`) na fileira 1; exemplos: cartão virando, tooltip apontando,
   leitura aberta, guia aberto.
3. Versos: 5 por tela (cartões da §0.2); régua só nos indicadores; origem com a célula (`docs/02`, tabela de
   passos).
4. Tooltips pelo mapa do brief (§2 do brief): T02 item do quadradinho (`itens_ultimo_mes` por grupo; item sem
   linha anexada = estado vazio), degrau da composição (`composicao[]`), mês (`serie[]`: estoque, adiantamentos,
   crédito, desembolso, variação), indicador (`sinais`, faixa, peso, série de 6 meses); T03 mês da curva S /
   ritmo (`serie[].prev/exec` mês e acumulado, desvio, tendência; mês sem previsto = parcial), obra do avanço /
   linha do tempo (`inicio`, `termino_previsto`, `orcamento`, `tipo_orcamento`, status; a iniciar = `proximas[]`,
   orçamento legal cronograma); T04 mês da carteira (contribuição por obra = `obras[].serie[mes].resultado`;
   `ativos_nao_consumidos`), obra do resultado (série de 6, melhor e pior mês), mês do desembolso (previsto ×
   desembolsado por obra), obra do desembolso (histórico `serie[].desvio_desembolso` + `justificativa`).
5. Leituras: 4 por tela (T02 quadradinho, como se forma, mês a mês, sinais; T03 curva S, ritmo, avanço, linha do
   tempo; T04 mês a mês, por obra, desembolso da carteira, desembolso por obra), gramática da §1.7, recorte REDINHA
   nas T02–03 e carteira na T04. Guia por tela com os marcadores.
6. Conferir cada peça em PNG (tamanho natural para verso/tooltip; 1920 para telas) antes de fechar; números só
   do JSON; registrar na spec os campos que faltarem.
